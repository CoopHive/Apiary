"""Unit tests for the Solver class and related functionality.

This module contains unit tests for the Solver class and other related components
such as Deal, Event, Job, Match, Result, Client, SmartContract, and Tx.
"""

# TODO: integrate them in pytest/CICD

import logging
import unittest

from coophive.deal import Deal
from coophive.event import Event
from coophive.job_offer import JobOffer
from coophive.match import Match
from coophive.resource_offer import ResourceOffer
from coophive.smart_contract import SmartContract
from coophive.solver import Solver


class TestSolver(unittest.TestCase):
    """Test suite for the Solver class."""

    def setUp(self):
        """Set up test environment for each test case."""
        self.public_key = "test_public_key"
        self.url = "http://test_url"
        self.solver = Solver(self.public_key, self.url)
        self.smart_contract = SmartContract("public_key_123")
        self.solver.connect_to_smart_contract(self.smart_contract)

        self.job_offer = JobOffer()
        self.job_offer.id = "job_offer_123"
        self.job_offer.set_attributes(
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

        self.resource_offer = ResourceOffer()
        self.resource_offer.id = "resource_offer_123"
        self.resource_offer.set_attributes(
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

        self.deal = Deal()
        self.deal.set_attributes(
            {
                "price_per_instruction": 10,
                "client_address": "client_address_123",
                "resource_provider_address": "resource_provider_address_123",
                "client_deposit": 300,
            }
        )

        self.match = Match()
        self.match.set_attributes(
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

        self.solver.get_local_information().add_job_offer(
            id="job_123", data=self.job_offer
        )
        self.solver.get_local_information().add_resource_offer(
            id="resource_123", data=self.resource_offer
        )

        logging.info("zyz", self.solver.get_local_information().ipfs.data)

    def test_connect_to_smart_contract(self):
        """Test connection to a smart contract."""
        self.solver.connect_to_smart_contract(self.smart_contract)
        self.assertEqual(self.solver.smart_contract, self.smart_contract)

    def test_handle_smart_contract_event_mediation_random(self):
        """Test handling of 'mediation_random' event from a smart contract."""
        event = Event("mediation_random", self.job_offer)
        self.solver.handle_smart_contract_event(event)
        self.assertIn(
            self.job_offer,
            self.solver.get_local_information().get_job_offers().values(),
        )

    def test_handle_smart_contract_event_deal(self):
        """Test handling of 'deal' event from a smart contract."""
        event = Event("deal", self.deal)
        self.solver.handle_smart_contract_event(event)
        self.assertIn(self.deal, self.solver.deals_made_in_current_step.values())

    def test_remove_outdated_offers(self):
        """Test removal of outdated offers."""
        self.solver.deals_made_in_current_step = [self.deal]
        self.solver.remove_outdated_offers()
        self.assertNotIn(
            "job_offer_123", self.solver.get_local_information().get_job_offers()
        )
        self.assertNotIn(
            "resource_offer_123",
            self.solver.get_local_information().get_resource_offers(),
        )

    def test_solver_cleanup(self):
        """Test solver cleanup process."""
        self.solver.currently_matched_job_offers = {"job_offer_123"}
        self.solver.current_matched_resource_offers = {"resource_offer_123"}
        self.solver.deals_made_in_current_step = [self.deal]
        self.solver.solver_cleanup()
        self.assertFalse(self.solver.currently_matched_job_offers)
        self.assertFalse(self.solver.current_matched_resource_offers)
        self.assertFalse(self.solver.deals_made_in_current_step)

    def test_solve(self):
        """Test the solve method of the solver."""
        self.solver.solve()
        self.assertIn("job_123", self.solver.currently_matched_job_offers)
        self.assertIn("resource_offer_123", self.solver.current_matched_resource_offers)

    def test_match_job_offer(self):
        """Test matching a job offer to a resource offer."""
        result = self.solver.match_job_offer(self.job_offer)
        self.assertEqual(result, self.resource_offer)

    def test_create_match(self):
        """Test creation of a match between job and resource offers."""
        match = self.solver.create_match(self.job_offer, self.resource_offer)
        self.assertEqual(
            match.get_data()["resource_provider_address"], "resource_owner_public_key"
        )
        self.assertEqual(match.get_data()["client_address"], "owner_123")
        self.assertEqual(match.get_data()["resource_offer"], "resource_offer_123")
        self.assertEqual(match.get_data()["job_offer"], "job_offer_123")


if __name__ == "__main__":
    unittest.main()
