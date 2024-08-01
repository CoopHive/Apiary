import pytest

from coophive.deal import Deal
from coophive.event import Event
from coophive.job_offer import JobOffer
from coophive.match import Match
from coophive.resource_offer import ResourceOffer
from coophive.smart_contract import SmartContract
from coophive.solver import Solver


@pytest.fixture
def setup_solver():
    """Fixture to set up the Solver and related objects."""
    public_key = "test_public_key"
    url = "http://test_url"
    solver = Solver(public_key, url)
    smart_contract = SmartContract("public_key_123")
    solver.connect_to_smart_contract(smart_contract)

    job_offer = JobOffer()
    job_offer.id = "job_offer_123"
    job_offer.set_attributes(
        {
            "owner": "owner_123",
            "target_client": "target_client_123",
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
            "owner": "resource_owner_public_key",
            "machine_id": "machine_12345",
            "target_client": "target_client_id",
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
            "client_address": "client_address_123",
            "resource_provider_address": "resource_provider_address_123",
            "client_deposit": 300,
        }
    )

    match = Match()
    match.set_attributes(
        {
            "resource_provider_address": "provider1",
            "client_address": "client1",
            "resource_offer": "offer1",
            "job_offer": "job1",
            "price_per_instruction": 10,
            "client_deposit": 100,
            "timeout": 10,
            "timeout_deposit": 15,
            "cheating_collateral_multiplier": 1.5,
            "verification_method": "method1",
            "mediators": ["mediator1", "mediator2"],
        }
    )

    solver.get_local_information().add_job_offer(id="job_123", data=job_offer)
    solver.get_local_information().add_resource_offer(
        id="resource_123", data=resource_offer
    )

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
    assert job_offer in solver.get_local_information().get_job_offers().values()


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
    assert "job_offer_123" not in solver.get_local_information().get_job_offers()
    assert (
        "resource_offer_123" not in solver.get_local_information().get_resource_offers()
    )


def test_solver_cleanup(setup_solver):
    """Test solver cleanup process."""
    solver = setup_solver["solver"]
    solver.currently_matched_job_offers = {"job_offer_123"}
    solver.current_matched_resource_offers = {"resource_offer_123"}
    solver.deals_made_in_current_step = [setup_solver["deal"]]
    solver.solver_cleanup()
    assert not solver.currently_matched_job_offers
    assert not solver.current_matched_resource_offers
    assert not solver.deals_made_in_current_step


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
    assert match.get_data()["resource_provider_address"] == "resource_owner_public_key"
    assert match.get_data()["client_address"] == "owner_123"
    assert match.get_data()["resource_offer"] == "resource_offer_123"
    assert match.get_data()["job_offer"] == "job_offer_123"


if __name__ == "__main__":
    pytest.main()
