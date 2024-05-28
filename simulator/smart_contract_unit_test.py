import unittest
from unittest.mock import MagicMock
from utils import *
from service_provider import ServiceProvider
from service_provider_local_information import LocalInformation
from collections import deque
from job import Job
from solver import Solver
from match import Match
from smart_contract import SmartContract
#JSON logging
from log_json import log_json
import logging
import os
from event import Event
from deal import Deal
from result import Result
from client import Client

class TestSmartContract(unittest.TestCase):

    def setUp(self):
        self.smart_contract = SmartContract("public_key")
        self.tx = Tx("sender", 100)
        
    def test_initial_balance(self):
        self.assertEqual(self.smart_contract._get_balance(), 0)
        
    def test_fund(self):
        self.tx.value = 200
        self.smart_contract.fund(self.tx)
        self.assertEqual(self.smart_contract.balances["sender"], 200)
        self.assertEqual(self.smart_contract._get_balance(), 0)
        
    def test_agree_to_match_resource_provider(self):
        match = Match()
        match.set_attributes({
            'timeout_deposit': 100,
            'resource_provider_address': 'provider_address'
        })
        
        self.tx.value = 100
        self.tx.sender = 'provider_address'
        self.smart_contract.balances['provider_address'] = 150
        
        
        self.smart_contract._agree_to_match_resource_provider(match, self.tx)
        self.assertEqual(self.smart_contract.balances['provider_address'], 50)
        self.assertEqual(self.smart_contract._get_balance(), 100)
        self.assertTrue(match.get_resource_provider_signed())
    
    def test_agree_to_match_client(self):
        match = Match()
        match.set_attributes({
            'client_deposit': 100,
            'client_address': 'client_address'
        })
        self.tx.value = 100
        self.tx.sender = 'client_address'
        self.smart_contract.balances['client_address'] = 150
        match.sign_client = MagicMock()
        
        self.smart_contract._agree_to_match_client(match, self.tx)
        self.assertEqual(self.smart_contract.balances['client_address'], 50)
        self.assertEqual(self.smart_contract._get_balance(), 100)
        match.sign_client.assert_called_once()
        
    def test_agree_to_match(self):
        match = Match()
        match.set_attributes({
            'timeout_deposit': 100,
            'resource_provider_address': 'provider_address',
            'client_deposit': 100,
            'client_address': 'client_address'
        })
        self.tx.value = 100
        self.tx.sender = 'provider_address'
        self.smart_contract.balances['provider_address'] = 150
        self.smart_contract.balances['client_address'] = 150
        
        self.smart_contract.agree_to_match(match, self.tx)
        self.assertEqual(self.smart_contract.balances['provider_address'], 50)
        self.assertEqual(self.smart_contract._get_balance(), 100)
        
        self.tx.sender = 'client_address'
        self.smart_contract.agree_to_match(match, self.tx)
        self.assertEqual(self.smart_contract.balances['client_address'], 50)
        self.assertEqual(self.smart_contract._get_balance(), 200)
        self.assertIn(match, self.smart_contract.matches_made_in_current_step)
        
    def test_create_deal(self):
        match = Match()
        match.set_attributes({
        'resource_provider_address': 'provider_address',
        'client_address': 'client_address'
        })
        self.smart_contract._create_deal(match)
        self.assertEquals(1, len(self.smart_contract.deals))   
    
    def test_post_result(self):
        result = Result()
        self.smart_contract.post_result(result, self.tx)
        self.assertIn([result, self.tx], self.smart_contract.results_posted_in_current_step)
        
    def test_refund_client_deposit(self):
        deal = Deal()
        deal.set_attributes({
            'client_address': 'client_address',
            'client_deposit': 100
        })
        self.smart_contract.balances['client_address'] = 0
        self.smart_contract._refund_client_deposit(deal)
        self.assertEqual(self.smart_contract.balances['client_address'], 100)
        self.assertEqual(self.smart_contract._get_balance(), -100)
        
    
if __name__ == "__main__":
    unittest.main()
