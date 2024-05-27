import unittest
from unittest.mock import MagicMock
from client import Client
from solver import Solver
from smart_contract import SmartContract
from job import Job
from match import Match
from utils import Tx
from resource_offer import ResourceOffer
from job_offer import JobOffer
from resource_provider import ResourceProvider
import testing_helper_functions
from deal import Deal
from event import Event
from result import Result
from collections import deque


class TestClient(unittest.TestCase):

    def setUp(self):
        self.client = Client(address="client_key")
        self.smart_contract = SmartContract(public_key="smart_contract_key")
        self.client.get_smart_contract = lambda: self.smart_contract
        self.match = Match()
        self.smart_contract.balances = {'client_key': 1000, 'resource_key': 500}
        self.client._create_transaction = lambda value: Tx(sender=self.client.get_public_key(), value=value)

    def test_get_solver(self):
        solver = Solver(public_key="solver_key", url="http://solver.com")
        self.client.connect_to_solver(url="http://solver.com", solver=solver)
        self.assertEqual(self.client.get_solver(), solver)

    def test_get_smart_contract(self):
        self.assertEqual(self.client.get_smart_contract(), self.smart_contract)

    def test_connect_to_solver(self):
        solver = Solver(public_key="solver_key", url="http://solver.com")
        self.client.connect_to_solver(url="http://solver.com", solver=solver)
        self.assertEqual(self.client.solver_url, "http://solver.com")
        self.assertEqual(self.client.solver, solver)

    def test_add_job(self):
        job = Job()
        self.client.add_job(job)
        self.assertIn(job, self.client.current_jobs)

    def test_get_jobs(self):
        job1 = Job()
        job2 = Job()
        self.client.add_job(job1)
        self.client.add_job(job2)
        self.assertEqual(self.client.get_jobs(), [job1, job2])

    def test_agree_to_match_happy_path(self):

        self.match.set_attributes({
            'client_deposit': 100,
            'client_address': 'client_key',
            'resource_provider_address': 'resource_key',
        })

        self.client._agree_to_match(self.match)

        self.assertEqual(self.smart_contract.balances['client_key'], 900)
        self.assertEqual(self.smart_contract.balance, 100)
        self.assertTrue(self.match.get_client_signed())
        self.assertFalse(self.match.get_resource_provider_signed())
    
    def test_agree_to_match_client_deposit_exceeds_balance(self):

        self.match.set_attributes({
            'client_deposit': 2000,
            'client_address': 'client_key',
            'resource_provider_address': 'resource_key',
        })

        with self.assertRaises(Exception) as context:
            self.client._agree_to_match(self.match)

        self.assertEqual(str(context.exception), "transaction value exceeds balance")

    def test_handle_solver_event(self):
        match = Match()
        match.set_attributes({'client_address': "client_key"})
        event = Event(name="match", data=match)
        self.client.handle_solver_event(event)
        self.assertIn(match, self.client.current_matched_offers)
        
    def test_pay_compute_node(self):
        
        self.client = Client("client_address_123")
        self.client.smart_contract = SmartContract("public_key_123")
        self.client.smart_contract.balances = {"client_address_123": 2000, "resource_provider_address_123": 0}
        self.client.smart_contract.balance = 0
        
        deal_id = "deal_123"
        instruction_count = 100
        price_per_instruction = 10
        client_address = "client_address_123"
        resource_provider_address = "resource_provider_address_123"
        tx_value = instruction_count * price_per_instruction

        # Define deal data
        deal_data = {
            'price_per_instruction': price_per_instruction,
            'client_address': client_address,
            'resource_provider_address': resource_provider_address,
            'client_deposit': 300
        }
        

        # Create a deal and add it to current deals
        deal = Deal()
        deal.set_attributes(deal_data)
        self.client.current_deals[deal_id] = deal
        self.smart_contract.deals[deal_id] = deal
        
        # Create event data
        result = Result()
        result_data = {
            'deal_id': deal_id,
            'instruction_count': instruction_count
        }
        result.set_attributes(result_data)
        
    
        # Create an event
        event = Event('event_1', data = result)
        
        print(self.client.smart_contract.balances.get("client_address_123"))
        
        # Call the method
        self.client.pay_compute_node(event=event)
        
        print(self.client.smart_contract.balances.get("client_address_123"))

        # Ensure balances are updated correctly
        self.assertEqual(self.client.smart_contract.balances.get("client_address_123", 0), float(2000 - tx_value + 300))
        self.assertEqual(self.client.smart_contract.balances.get("resource_provider_address_123", 0), tx_value)


    def test_update_finished_deals(self):
        self.client.current_deals = {'deal1': MagicMock(), 'deal2': MagicMock()}
        self.client.deals_finished_in_current_step = ['deal1']

        self.client.update_finished_deals()
        self.assertNotIn('deal1', self.client.current_deals)  # check if 'deal1' is removed
        self.assertIn('deal2', self.client.current_deals)  # check if 'deal2' is still present
        self.assertEqual(len(self.client.deals_finished_in_current_step), 0)  # check if deals_finished_in_current_step is cleared

    def test_client_loop(self):
                
        match1 = Match()

        match1.set_attributes({
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
            "mediators": ["mediator1", "mediator2"]
        })

        match2 = Match()

        match2.set_attributes({
            "resource_provider_address": "provider2",
            "client_address": "client2",
            "resource_offer": "offer2",
            "job_offer": "job2",
            "price_per_instruction": 50,
            "client_deposit": 100,
            "timeout": 12,
            "timeout_deposit": 20,
            "cheating_collateral_multiplier": 1.0,
            "verification_method": "method2",
            "mediators": ["mediator3"]
        })

        self.client.current_matched_offers.append(match1)
        self.client.current_matched_offers.append(match2)
        
        self.client._agree_to_match = MagicMock()
        self.client.update_finished_deals = MagicMock()

        self.client.client_loop()
        self.assertEqual(self.client._agree_to_match.call_count, 0)
        self.assertEqual(self.client.update_finished_deals.call_count, 1)
        self.assertEqual(len(self.client.current_matched_offers), 0)

if __name__ == "__main__":
    unittest.main()
