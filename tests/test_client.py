from unittest.mock import MagicMock, patch

import pytest

from coophive.client import Client
from coophive.deal import Deal
from coophive.event import Event
from coophive.job import Job
from coophive.match import Match
from coophive.policy import Policy
from coophive.result import Result
from coophive.smart_contract import SmartContract
from coophive.solver import Solver
from coophive.utils import Tx

mock_private_key = "0x4c0883a69102937d6231471b5dbb6204fe512961708279a4a6075d78d6d3721b"
mock_public_key = "0x627306090abaB3A6e1400e9345bC60c78a8BEf57"
policy_a = Policy("naive_accepter")
solver_url = "http://solver.com"


@pytest.fixture
def setup_client():
    """Fixture to set up the test environment."""
    # patch the socket to avoid the need to connect to the server.
    with patch("socket.socket") as mock_socket:
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        client = Client(
            private_key=mock_private_key, public_key=mock_public_key, policy=policy_a
        )
        smart_contract = SmartContract(public_key="smart_contract_key")
        client.get_smart_contract = lambda: smart_contract
        match = Match()
        smart_contract.balances = {"client_key": 1000, "resource_key": 500}
        client._create_transaction = lambda value: Tx(
            sender=client.get_public_key(), value=value
        )
        return client, smart_contract, match


def test_get_smart_contract(setup_client):
    """Test the get_smart_contract method."""
    client, smart_contract, _ = setup_client
    assert client.get_smart_contract() == smart_contract


def test_connect_to_solver(setup_client):
    """Test the connect_to_solver method."""
    client, _, _ = setup_client

    solver = Solver(
        private_key=mock_private_key,
        public_key=mock_public_key,
        policy=policy_a,
        solver_url=solver_url,
    )

    client.connect_to_solver(solver_url=solver_url, solver=solver)
    assert client.solver_url == solver_url
    assert client.solver == solver


def test_add_job(setup_client):
    """Test the add_job method."""
    client, _, _ = setup_client
    job = Job()
    client.add_job(job)
    assert job in client.current_jobs


def test_get_jobs(setup_client):
    """Test the get_jobs method."""
    client, _, _ = setup_client
    job1 = Job()
    job2 = Job()
    client.add_job(job1)
    client.add_job(job2)
    assert client.get_jobs() == [job1, job2]


def test_agree_to_match_happy_path(setup_client):
    """Test the _agree_to_match method with sufficient client balance."""
    client, smart_contract, match = setup_client
    match.set_attributes(
        {
            "client_deposit": 100,
            "client_address": "client_key",
            "resource_provider_address": "resource_key",
        }
    )

    client._agree_to_match(match)

    assert smart_contract.balances["client_key"] == 900
    assert smart_contract.balance == 100
    assert match.get_client_signed()
    assert not match.get_resource_provider_signed()


def test_agree_to_match_client_deposit_exceeds_balance(setup_client):
    """Test the _agree_to_match method with insufficient client balance."""
    client, _, match = setup_client
    match.set_attributes(
        {
            "client_deposit": 2000,
            "client_address": "client_key",
            "resource_provider_address": "resource_key",
        }
    )

    with pytest.raises(Exception, match="transaction value exceeds balance"):
        client._agree_to_match(match)


def test_handle_solver_event(setup_client):
    """Test the handle_solver_event method."""
    client, _, _ = setup_client
    match = Match()
    match.set_attributes({"client_address": "client_key"})
    event = Event(name="match", data=match)
    client.handle_solver_event(event)
    assert match in client.current_matched_offers


def test_pay_compute_node():
    """Test the pay_compute_node method."""
    # patch the socket to avoid the need to connect to the server.
    with patch("socket.socket") as mock_socket:
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        client = Client("client_address_123", policy_a)
        client.smart_contract = SmartContract("public_key_123")
        client.smart_contract.balances = {
            "client_address_123": 2000,
            "resource_provider_address_123": 0,
        }
        client.smart_contract.balance = 0

        deal_id = "deal_123"
        instruction_count = 100
        price_per_instruction = 10
        client_address = "client_address_123"
        resource_provider_address = "resource_provider_address_123"
        tx_value = instruction_count * price_per_instruction

        # Define deal data
        deal_data = {
            "price_per_instruction": price_per_instruction,
            "client_address": client_address,
            "resource_provider_address": resource_provider_address,
            "client_deposit": 300,
        }

        # Create a deal and add it to current deals
        deal = Deal()
        deal.set_attributes(deal_data)
        client.current_deals[deal_id] = deal
        client.smart_contract.deals[deal_id] = deal

        # Create event data
        result = Result()
        result_data = {"deal_id": deal_id, "instruction_count": instruction_count}
        result.set_attributes(result_data)

        # Create an event
        event = Event("event_1", data=result)

        # Call the method
        client.pay_compute_node(event=event)

        # Ensure balances are updated correctly
        assert client.smart_contract.balances.get("client_address_123", 0) == float(
            2000 - tx_value + 300
        )
        assert (
            client.smart_contract.balances.get("resource_provider_address_123", 0)
            == tx_value
        )


def test_update_finished_deals(setup_client):
    """Test the update_finished_deals method."""
    client, _, _ = setup_client
    client.current_deals = {"deal1": MagicMock(), "deal2": MagicMock()}
    client.deals_finished_in_current_step = ["deal1"]

    client.update_finished_deals()
    assert "deal1" not in client.current_deals  # check if 'deal1' is removed
    assert "deal2" in client.current_deals  # check if 'deal2' is still present
    assert (
        len(client.deals_finished_in_current_step) == 0
    )  # check if deals_finished_in_current_step is cleared


def test_client_loop(setup_client):
    """Test the client_loop method."""
    client, _, _ = setup_client
    match1 = Match()
    match1.set_attributes(
        {
            "resource_provider_address": "provider1",
            "client_address": "client1",
            "resource_offer": {
                "owner": "provider1",
                "machine_id": "machine1",
                "target_client": "client1",
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
                "owner": "client1",
                "target_client": "client1",
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
                "benefit_to_client": 2000,
                "T_accept": 50,
                "T_reject": 20,
            },
            "price_per_instruction": 10,
            "expected_number_of_instructions": 1000,
            "expected_benefit_to_client": 2000,
            "client_deposit": 100,
            "timeout": 10,
            "timeout_deposit": 15,
            "cheating_collateral_multiplier": 1.5,
        }
    )

    match2 = Match()
    match2.set_attributes(
        {
            "resource_provider_address": "provider2",
            "client_address": "client2",
            "resource_offer": {
                "owner": "provider2",
                "machine_id": "machine2",
                "target_client": "client2",
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
                "owner": "client2",
                "target_client": "client2",
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
                "benefit_to_client": 3000,
                "T_accept": 70,
                "T_reject": 30,
            },
            "price_per_instruction": 50,
            "expected_number_of_instructions": 2000,
            "expected_benefit_to_client": 3000,
            "client_deposit": 100,
            "timeout": 12,
            "timeout_deposit": 20,
            "cheating_collateral_multiplier": 1.0,
        }
    )

    client.current_matched_offers.append(match1)
    client.current_matched_offers.append(match2)

    client._agree_to_match = MagicMock()
    client.update_finished_deals = MagicMock()

    client.client_loop()

    assert client.update_finished_deals.call_count == 1
    assert len(client.current_matched_offers) == 0


if __name__ == "__main__":
    pytest.main()
