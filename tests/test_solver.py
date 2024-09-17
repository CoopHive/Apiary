import pytest

from coophive.deal import Deal
from coophive.event import Event
from coophive.job_offer import JobOffer
from coophive.match import Match
from coophive.resource_offer import ResourceOffer
from coophive.smart_contract import SmartContract
from coophive.solver import Solver

private_key_solver = (
    "0x4c0883a69102937d6231471b5dbb6204fe512961708279a4a6075d78d6d3721b"
)
public_key_solver = "0x627306090abaB3A6e1400e9345bC60c78a8BEf57"

policy_solver = "mock_policy"


@pytest.fixture
def setup_solver():
    """Fixture to set up the Solver and related objects."""

    solver = Solver(
        private_key=private_key_solver,
        public_key=public_key_solver,
        policy_name=policy_solver,
    )

    smart_contract = SmartContract("public_key_123")
    solver.connect_to_smart_contract(smart_contract)

    job_offer = JobOffer()
    job_offer.id = "job_offer_123"
    job_offer.set_attributes(
        {
            "owner": "owner_123",
            "target_buyer": "target_buyer_123",
            "created_at": "2024",
            "timeout": "123",
            "CPU": 8,
            "GPU": 2,
            "RAM": 16,
            "module": None,
            "prices": {"CPU": 8, "GPU": 13},
            "verification_method": None,
            "mediators": ["mediator_1", "mediator_2"],
        }
    )

    resource_offer = ResourceOffer()
    resource_offer.id = "resource_offer_123"
    resource_offer.set_attributes(
        {
            "owner": "seller_public_key",
            "machine_id": "machine_12345",
            "target_buyer": "target_buyer_id",
            "created_at": "2024-05-28T12:00:00Z",
            "timeout": 3600,
            "CPU": 8,
            "GPU": 2,
            "RAM": 16,
            "prices": {"CPU": 0.4, "GPU": 0.9, "RAM": 0.15},
            "verification_method": "signature_verification",
            "mediators": ["mediator1", "mediator2"],
        }
    )

    deal = Deal()
    deal.set_attributes(
        {
            "price_per_instruction": 10,
            "buyer_address": "buyer_address_123",
            "seller_address": "seller_address_123",
            "buyer_deposit": 300,
        }
    )

    match = Match()
    match.set_attributes(
        {
            "seller_address": "provider1",
            "buyer_address": "buyer1",
            "resource_offer": "offer1",
            "job_offer": "job1",
            "price_per_instruction": 10,
            "buyer_deposit": 100,
            "timeout": 10,
            "timeout_deposit": 15,
            "cheating_collateral_multiplier": 1.5,
            "verification_method": "method1",
            "mediators": ["mediator1", "mediator2"],
        }
    )

    solver.local_information.add_job_offer(id="job_123", data=job_offer)
    solver.local_information.add_resource_offer(id="resource_123", data=resource_offer)

    return {
        "solver": solver,
        "smart_contract": smart_contract,
        "job_offer": job_offer,
        "resource_offer": resource_offer,
        "deal": deal,
        "match": match,
    }


def test_connect_to_smart_contract(setup_solver):
    """Test connection to a smart contract."""
    solver = setup_solver["solver"]
    smart_contract = setup_solver["smart_contract"]
    solver.connect_to_smart_contract(smart_contract)
    assert solver.smart_contract == smart_contract


def test_handle_smart_contract_event_mediation_random(setup_solver):
    """Test handling of 'mediation_random' event from a smart contract."""
    solver = setup_solver["solver"]
    job_offer = setup_solver["job_offer"]
    event = Event("mediation_random", job_offer)
    solver.handle_smart_contract_event(event)
    assert job_offer in solver.local_information.job_offers.values()


def test_handle_smart_contract_event_deal(setup_solver):
    """Test handling of 'deal' event from a smart contract."""
    solver = setup_solver["solver"]
    deal = setup_solver["deal"]
    event = Event("deal", deal)
    solver.handle_smart_contract_event(event)
    assert deal in solver.deals_made_in_current_step.values()


def test_remove_outdated_offers(setup_solver):
    """Test removal of outdated offers."""
    solver = setup_solver["solver"]
    solver.deals_made_in_current_step = [setup_solver["deal"]]
    solver.remove_outdated_offers()
    assert "job_offer_123" not in solver.local_information.job_offers
    assert "resource_offer_123" not in solver.local_information.resource_offers


def test_solve(setup_solver):
    """Test the solve method of the solver."""
    solver = setup_solver["solver"]
    solver.solve()
    assert "job_123" in solver.currently_matched_job_offers
    assert "resource_offer_123" in solver.current_matched_resource_offers


def test_match_job_offer(setup_solver):
    """Test matching a job offer to a resource offer."""
    solver = setup_solver["solver"]
    job_offer = setup_solver["job_offer"]
    result = solver.match_job_offer(job_offer)
    assert result == setup_solver["resource_offer"]


def test_create_match(setup_solver):
    """Test creation of a match between job and resource offers."""
    solver = setup_solver["solver"]
    job_offer = setup_solver["job_offer"]
    resource_offer = setup_solver["resource_offer"]
    match = solver.create_match(job_offer, resource_offer)
    assert match.get_data()["seller_address"] == "seller_public_key"
    assert match.get_data()["buyer_address"] == "owner_123"
    assert match.get_data()["resource_offer"] == "resource_offer_123"
    assert match.get_data()["job_offer"] == "job_offer_123"


if __name__ == "__main__":
    pytest.main()
