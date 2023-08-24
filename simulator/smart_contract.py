from utils import *
from service_provider import ServiceProvider
from event import Event
from match import Match
from deal import Deal
from result import Result


class SmartContract(ServiceProvider):
    def __init__(self, public_key: str):
        super().__init__(public_key)
        self.transactions = []
        self.deals = {}  # mapping from deal id to deal
        self.balances = {}  # mapping from public key to balance
        self.balance = 0  # total balance in the contract

    def _agree_to_match_resource_provider(self, match: Match, tx: Tx):
        match_data = match.get_data()
        timeout_deposit = match_data['timeout_deposit']
        if tx.value != timeout_deposit:
            print()
            print(f'transaction value of {tx.value} does not match timeout deposit {match_data["timeout_deposit"]}')
            raise Exception("transaction value does not match timeout deposit")
        self.balances[match.get_data()['resource_provider_address']] -= timeout_deposit
        self.balance += timeout_deposit
        match.sign_resource_provider()
        print('rp has signed')
        print(self.balances)
        print(self.balance)

    def _agree_to_match_client(self, match: Match, tx: Tx):
        match_data = match.get_data()
        client_deposit = match_data['client_deposit']
        if tx.value != client_deposit:
            print()
            print(f'transaction value of {tx.value} does not match client deposit {match_data["client_deposit"]}')
            raise Exception("transaction value does not match timeout deposit")
        self.balances[match.get_data()['client_address']] -= tx.value
        self.balance += tx.value
        match.sign_client()
        print('client has signed')
        print(self.balances)
        print(self.balance)

    def agree_to_match(self, match: Match, tx: Tx):
        if match.get_data()['resource_provider_address'] == tx.sender:
            self._agree_to_match_resource_provider(match, tx)
        elif match.get_data()['client_address'] == tx.sender:
            self._agree_to_match_client(match, tx)
        if match.get_resource_provider_signed() and match.get_client_signed():
            print('both rp and client have signed')
            self._create_deal(match)
            print("match attributes:", match.get_data())

    def _create_deal(self, match):
        deal = Deal()
        for data_field, data_value in match.get_data().items():
            deal.add_data(data_field, data_value)
        # todo: this is for testing purposes, should not be added here manually
        deal.add_data('actual_honest_time_to_completion', 1)
        deal.set_id()
        self.deals[deal.get_id()] = deal
        deal_event = Event(name='deal', data=deal)
        self.emit_event(deal_event)
        print("deal attributes:", deal.get_data())

    def _refund_timeout_deposit(self, result: Result):
        deal_id = result.get_data()['deal_id']
        deal_data = self.deals[deal_id].get_data()
        timeout_deposit = deal_data['timeout_deposit']
        resource_provider_address = deal_data['resource_provider_address']
        self.balances[resource_provider_address] += timeout_deposit
        self.balance -= timeout_deposit
        print()
        print(self.balances)
        print(self.balance)

    def _post_cheating_collateral(self, result: Result, tx: Tx):
        deal_id = result.get_data()['deal_id']
        cheating_collateral_multiplier = self.deals[deal_id].get_data()['cheating_collateral_multiplier']
        instruction_count = result.get_data()['instruction_count']
        intended_cheating_collateral = cheating_collateral_multiplier * instruction_count
        if cheating_collateral_multiplier * instruction_count != tx.value:
            print()
            print(f'transaction value of {tx.value} does not match needed cheating collateral deposit {intended_cheating_collateral}')
            raise Exception("transaction value does not match needed cheating collateral")
        self.balance += tx.value

    def post_result(self, result: Result, tx: Tx):
        deal_id = result.get_data()['deal_id']
        if self.deals[deal_id].get_data()['resource_provider_address'] == tx.sender:
            result_event = Event(name='result', data=result)
            self.emit_event(result_event)
            self._refund_timeout_deposit(result)

    # def post_client_payment(self, result: Result, tx: Tx):

    def fund(self, tx: Tx):
        self.balances[tx.sender] = self.balances.get(tx.sender, 0) + tx.value
        print(self.balances)
