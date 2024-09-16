from unittest.mock import MagicMock, patch

import pytest

from coophive.buyer import Buyer
from coophive.deal import Deal
from coophive.event import Event
from coophive.match import Match
from coophive.result import Result
from coophive.smart_contract import SmartContract
from coophive.utils import Tx

private_key_buyer = "0x4c0883a69102937d6231471b5dbb6204fe512961708279a4a6075d78d6d3721b"
public_key_buyer = "0x627306090abaB3A6e1400e9345bC60c78a8BEf57"
public_key_seller = "0x627306090abaB3A6e1400e9345bC60c78a8BEf56"

policy_a = "naive_accepter"


@pytest.fixture
def setup_buyer():
    """Fixture to set up the test environment."""
    # patch the socket to avoid the need to connect to the server.
    with patch("socket.socket") as mock_socket:
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        buyer = Buyer(
            private_key=private_key_buyer,
            public_key=public_key_buyer,
            policy_name=policy_a,
        )
        smart_contract = SmartContract(public_key="smart_contract_key")
        buyer.get_smart_contract = lambda: smart_contract
        match = Match()
        smart_contract.balances = {
            public_key_buyer: 1000,
            public_key_seller: 500,
        }
        buyer._create_transaction = lambda value: Tx(
            sender=buyer.get_public_key(), value=value
        )
        return buyer, smart_contract, match


def test_get_smart_contract(setup_buyer):
    """Test the get_smart_contract method."""
    buyer, smart_contract, _ = setup_buyer
    assert buyer.get_smart_contract() == smart_contract


def test_agree_to_match_happy_path(setup_buyer):
    """Test the _agree_to_match method with sufficient buyer balance."""
    buyer, smart_contract, match = setup_buyer
    match.set_attributes(
        {
            "buyer_deposit": 100,
            "buyer_address": public_key_buyer,
            "seller_address": public_key_seller,
        }
    )

    buyer._agree_to_match(match)

    assert smart_contract.balances[public_key_buyer] == 900
    assert smart_contract.balances[public_key_seller] == 500
    assert smart_contract.balance == 100
    assert match.get_buyer_signed()
    assert not match.get_seller_signed()


def test_agree_to_match_buyer_deposit_exceeds_balance(setup_buyer):
    """Test the _agree_to_match method with insufficient buyer balance."""
    buyer, _, match = setup_buyer
    match.set_attributes(
        {
            "buyer_deposit": 2000,
            "buyer_address": public_key_buyer,
            "seller_address": public_key_seller,
        }
    )

    with pytest.raises(Exception, match="transaction value exceeds balance"):
        buyer._agree_to_match(match)


def test_handle_solver_event(setup_buyer):
    """Test the handle_solver_event method."""
    buyer, _, _ = setup_buyer
    match = Match()
    match.set_attributes({"buyer_address": public_key_buyer})
    event = Event(name="match", data=match)
    buyer.handle_solver_event(event)
    assert match in buyer.current_matched_offers


def test_pay_compute_node():
    """Test the pay_compute_node method."""
    # patch the socket to avoid the need to connect to the server.
    with patch("socket.socket") as mock_socket:
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        buyer = Buyer(
            private_key=private_key_buyer,
            public_key=public_key_buyer,
            policy_name=policy_a,
        )

        buyer.smart_contract = SmartContract("public_key_123")
        buyer.smart_contract.balances = {
            public_key_buyer: 2000,
            public_key_seller: 0,
        }
        buyer.smart_contract.balance = 0

        deal_id = "deal_123"
        instruction_count = 100
        price_per_instruction = 10
        tx_value = instruction_count * price_per_instruction

        # Define deal data
        deal_data = {
            "price_per_instruction": price_per_instruction,
            "buyer_address": public_key_buyer,
            "seller_address": public_key_seller,
            "buyer_deposit": 300,
        }

        # Create a deal and add it to current deals
        deal = Deal()
        deal.set_attributes(deal_data)
        buyer.current_deals[deal_id] = deal
        buyer.smart_contract.deals[deal_id] = deal

        # Create event data
        result = Result()
        result_data = {"deal_id": deal_id, "instruction_count": instruction_count}
        result.set_attributes(result_data)

        # Create an event
        event = Event("event_1", data=result)

        # Call the method
        buyer.pay_compute_node(event=event)

        # Ensure balances are updated correctly
        assert buyer.smart_contract.balances.get(public_key_buyer, 0) == float(
            2000 - tx_value + 300
        )
        assert buyer.smart_contract.balances.get(public_key_seller, 0) == tx_value


def test_update_finished_deals(setup_buyer):
    """Test the update_finished_deals method."""
    buyer, _, _ = setup_buyer
    buyer.current_deals = {"deal1": MagicMock(), "deal2": MagicMock()}
    buyer.deals_finished_in_current_step = ["deal1"]

    buyer.update_finished_deals()
    assert "deal1" not in buyer.current_deals  # check if 'deal1' is removed
    assert "deal2" in buyer.current_deals  # check if 'deal2' is still present
    assert (
        len(buyer.deals_finished_in_current_step) == 0
    )  # check if deals_finished_in_current_step is cleared


def test_buyer_loop(setup_buyer):
    """Test the buyer_loop method."""
    buyer, _, _ = setup_buyer
    match1 = Match()
    match1.set_attributes(
        {
            "seller_address": "provider1",
            "buyer_address": "buyer1",
            "resource_offer": {
                "owner": "provider1",
                "machine_id": "machine1",
                "target_buyer": "buyer1",
                "created_at": "2024-08-15",
                "timeout": 10,
                "CPU": 4,
                "GPU": 1,
                "RAM": 16,
                "prices": [10, 20, 30],
                "verification_method": "method1",
                "mediators": ["mediator1", "mediator2"],
                "price_per_instruction": 10,
                "expected_number_of_instructions": 1000,
                "T_accept": 50,
                "T_reject": 20,
            },
            "job_offer": {
                "owner": "buyer1",
                "target_buyer": "buyer1",
                "created_at": "2024-08-15",
                "timeout": 10,
                "CPU": 4,
                "GPU": 1,
                "RAM": 16,
                "module": "module1",
                "prices": [15, 25, 35],
                "instruction_count": 100,
                "verification_method": "method1",
                "mediators": ["mediator1", "mediator2"],
                "benefit_to_buyer": 2000,
                "T_accept": 50,
                "T_reject": 20,
            },
            "price_per_instruction": 10,
            "expected_number_of_instructions": 1000,
            "expected_benefit_to_buyer": 2000,
            "buyer_deposit": 100,
            "timeout": 10,
            "timeout_deposit": 15,
            "cheating_collateral_multiplier": 1.5,
        }
    )

    match2 = Match()
    match2.set_attributes(
        {
            "seller_address": "provider2",
            "buyer_address": "buyer2",
            "resource_offer": {
                "owner": "provider2",
                "machine_id": "machine2",
                "target_buyer": "buyer2",
                "created_at": "2024-08-15",
                "timeout": 12,
                "CPU": 8,
                "GPU": 2,
                "RAM": 32,
                "prices": [20, 40, 60],
                "verification_method": "method2",
                "mediators": ["mediator3"],
                "price_per_instruction": 50,
                "expected_number_of_instructions": 2000,
                "T_accept": 70,
                "T_reject": 30,
            },
            "job_offer": {
                "owner": "buyer2",
                "target_buyer": "buyer2",
                "created_at": "2024-08-15",
                "timeout": 12,
                "CPU": 8,
                "GPU": 2,
                "RAM": 32,
                "module": "module2",
                "prices": [25, 50, 75],
                "instruction_count": 100,
                "verification_method": "method2",
                "mediators": ["mediator3"],
                "benefit_to_buyer": 3000,
                "T_accept": 70,
                "T_reject": 30,
            },
            "price_per_instruction": 50,
            "expected_number_of_instructions": 2000,
            "expected_benefit_to_buyer": 3000,
            "buyer_deposit": 100,
            "timeout": 12,
            "timeout_deposit": 20,
            "cheating_collateral_multiplier": 1.0,
        }
    )

    buyer.current_matched_offers.append(match1)
    buyer.current_matched_offers.append(match2)

    buyer._agree_to_match = MagicMock()
    buyer.update_finished_deals = MagicMock()

    buyer.buyer_loop()

    assert buyer.update_finished_deals.call_count == 1
    assert len(buyer.current_matched_offers) == 0


if __name__ == "__main__":
    pytest.main()
