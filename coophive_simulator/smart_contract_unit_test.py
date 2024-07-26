"""Unit tests for the SmartContract class and related functionality.

This module contains unit tests for the SmartContract class and other related components
such as Deal, Event, Job, Match, Result, Client, Solver, and Tx.
"""

# TODO: integrate them in pytest/CICD

import unittest
from unittest.mock import MagicMock

from coophive_simulator.deal import Deal
from coophive_simulator.match import Match
from coophive_simulator.result import Result
from coophive_simulator.smart_contract import SmartContract
from coophive_simulator.utils import Tx


class TestSmartContract(unittest.TestCase):
    """Unit tests for the SmartContract class."""

    def setUp(self):
        """Set up the SmartContract instance and a transaction for testing."""
        self.smart_contract = SmartContract("public_key")
        self.tx = Tx("sender", 100)

    def test_initial_balance(self):
        """Test that the initial balance of the smart contract is zero."""
        self.assertEqual(self.smart_contract._get_balance(), 0)

    def test_fund(self):
        """Test the funding of the smart contract by a transaction."""
        self.tx.value = 200
        self.smart_contract.fund(self.tx)
        self.assertEqual(self.smart_contract.balances["sender"], 200)
        self.assertEqual(self.smart_contract._get_balance(), 0)

    def test_agree_to_match_resource_provider(self):
        """Test resource provider agreement to a match."""
        match = Match()
        match.set_attributes(
            {"timeout_deposit": 100, "resource_provider_address": "provider_address"}
        )

        self.tx.value = 100
        self.tx.sender = "provider_address"
        self.smart_contract.balances["provider_address"] = 150

        self.smart_contract._agree_to_match_resource_provider(match, self.tx)
        self.assertEqual(self.smart_contract.balances["provider_address"], 50)
        self.assertEqual(self.smart_contract._get_balance(), 100)
        self.assertTrue(match.get_resource_provider_signed())

    def test_agree_to_match_client(self):
        """Test client agreement to a match."""
        match = Match()
        match.set_attributes(
            {"client_deposit": 100, "client_address": "client_address"}
        )
        self.tx.value = 100
        self.tx.sender = "client_address"
        self.smart_contract.balances["client_address"] = 150
        match.sign_client = MagicMock()

        self.smart_contract._agree_to_match_client(match, self.tx)
        self.assertEqual(self.smart_contract.balances["client_address"], 50)
        self.assertEqual(self.smart_contract._get_balance(), 100)
        match.sign_client.assert_called_once()

    def test_agree_to_match(self):
        """Test both resource provider and client agreements to a match."""
        match = Match()
        match.set_attributes(
            {
                "timeout_deposit": 100,
                "resource_provider_address": "provider_address",
                "client_deposit": 100,
                "client_address": "client_address",
            }
        )
        self.tx.value = 100
        self.tx.sender = "provider_address"
        self.smart_contract.balances["provider_address"] = 150
        self.smart_contract.balances["client_address"] = 150

        self.smart_contract.agree_to_match(match, self.tx)
        self.assertEqual(self.smart_contract.balances["provider_address"], 50)
        self.assertEqual(self.smart_contract._get_balance(), 100)

        self.tx.sender = "client_address"
        self.smart_contract.agree_to_match(match, self.tx)
        self.assertEqual(self.smart_contract.balances["client_address"], 50)
        self.assertEqual(self.smart_contract._get_balance(), 200)
        self.assertIn(match, self.smart_contract.matches_made_in_current_step)

    def test_create_deal(self):
        """Test the creation of a deal."""
        match = Match()
        match.set_attributes(
            {
                "resource_provider_address": "provider_address",
                "client_address": "client_address",
            }
        )
        self.smart_contract._create_deal(match)
        self.assertEquals(1, len(self.smart_contract.deals))

    def test_post_result(self):
        """Test posting a result."""
        result = Result()
        self.smart_contract.post_result(result, self.tx)
        self.assertIn(
            [result, self.tx], self.smart_contract.results_posted_in_current_step
        )

    def test_refund_client_deposit(self):
        """Test refunding the client's deposit."""
        deal = Deal()
        deal.set_attributes({"client_address": "client_address", "client_deposit": 100})
        self.smart_contract.balances["client_address"] = 0
        self.smart_contract._refund_client_deposit(deal)
        self.assertEqual(self.smart_contract.balances["client_address"], 100)
        self.assertEqual(self.smart_contract._get_balance(), -100)


if __name__ == "__main__":
    unittest.main()
