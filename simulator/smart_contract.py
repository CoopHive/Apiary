from utils import *
from service_provider import ServiceProvider
from event import Event
from match import Match
from deal import Deal
from result import Result
import logging
import os


class SmartContract(ServiceProvider):
    def __init__(self, public_key: str):
        super().__init__(public_key)
        self.logger = logging.getLogger(f"Smart Contract {self.public_key}")
        logging.basicConfig(filename=f'{os.getcwd()}/local_logs', filemode='w', level=logging.DEBUG)
        self.transactions = []
        self.deals = {}  # mapping from deal id to deal
        self.balances = {}  # mapping from public key to balance
        self.balance = 0  # total balance in the contract
        self.matches_made_in_current_step = []
        self.results_posted_in_current_step = []

    def _agree_to_match_resource_provider(self, match: Match, tx: Tx):
        match_data = match.get_data()
        timeout_deposit = match_data['timeout_deposit']
        if tx.value != timeout_deposit:
            print()
            print(f'transaction value of {tx.value} does not match timeout deposit {match_data["timeout_deposit"]}')
            raise Exception("transaction value does not match timeout deposit")
        resource_provider_address = match_data['resource_provider_address']
        self.balances[resource_provider_address] -= timeout_deposit
        self.balance += timeout_deposit
        match.sign_resource_provider()
        self.logger.info(f"resource provider {match.get_data()['resource_provider_address']} has signed match {match.get_id()}")

    def _agree_to_match_client(self, match: Match, tx: Tx):
        match_data = match.get_data()
        client_deposit = match_data['client_deposit']
        if tx.value != client_deposit:
            print()
            print(f'transaction value of {tx.value} does not match client deposit {match_data["client_deposit"]}')
            raise Exception("transaction value does not match timeout deposit")
        client_address = match_data['client_address']
        if client_deposit > self.balances[client_address]:
            print()
            print(f'transaction value of {tx.value} exceeds client balance of {self.balances[client_address]}')
            raise Exception("transaction value exceeds balance")
        self.balances[client_address] -= tx.value
        self.balance += tx.value
        match.sign_client()
        self.logger.info(f"client {match.get_data()['client_address']} has signed match {match.get_id()}")

    def agree_to_match(self, match: Match, tx: Tx):
        if match.get_data()['resource_provider_address'] == tx.sender:
            self._agree_to_match_resource_provider(match, tx)
        elif match.get_data()['client_address'] == tx.sender:
            self._agree_to_match_client(match, tx)
        if match.get_resource_provider_signed() and match.get_client_signed():
            self.logger.info(f"both resource provider {match.get_data()['resource_provider_address']} and client {match.get_data()['client_address']} have signed match {match.get_id()}")
            self.logger.info(f"match attributes of match {match.get_id()}: {match.get_data()}")
            # self._create_deal(match)
            self.matches_made_in_current_step.append(match)

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
        self.logger.info(f"deal created; deal attributes:, {deal.get_data()}")
        # append to transactions
        self.transactions.append(deal_event)

    def _refund_timeout_deposit(self, result: Result):
        deal_id = result.get_data()['deal_id']
        deal_data = self.deals[deal_id].get_data()
        timeout_deposit = deal_data['timeout_deposit']
        resource_provider_address = deal_data['resource_provider_address']
        self.balances[resource_provider_address] += timeout_deposit
        self.balance -= timeout_deposit

    def _post_cheating_collateral(self, result: Result, tx: Tx):
        deal_id = result.get_data()['deal_id']
        deal_data = self.deals[deal_id].get_data()
        cheating_collateral_multiplier = deal_data['cheating_collateral_multiplier']
        instruction_count = result.get_data()['instruction_count']
        intended_cheating_collateral = cheating_collateral_multiplier * instruction_count
        if intended_cheating_collateral != tx.value:
            print(f'transaction value of {tx.value} does not match needed cheating collateral deposit {intended_cheating_collateral}')
            raise Exception("transaction value does not match needed cheating collateral")
        resource_provider_address = deal_data['resource_provider_address']
        if intended_cheating_collateral > self.balances[resource_provider_address]:
            print()
            print(f'transaction value of {tx.value} exceeds resource provider balance of {self.balances[resource_provider_address]}')
            raise Exception("transaction value exceeds balance")
        self.balances[resource_provider_address] -= tx.value
        self.balance += tx.value

    def _create_and_emit_result_events(self):
        for result, tx in self.results_posted_in_current_step:
            deal_id = result.get_data()['deal_id']
            if self.deals[deal_id].get_data()['resource_provider_address'] == tx.sender:
                result_event = Event(name='result', data=result)
                self.emit_event(result_event)
                self._refund_timeout_deposit(result)
                # append to transactions
                self.transactions.append(result_event)

    def _account_for_cheating_collateral_payments(self):
        for result, tx in self.results_posted_in_current_step:
            self._post_cheating_collateral(result, tx)

    def post_result(self, result: Result, tx: Tx):
        self.results_posted_in_current_step.append([result, tx])

    def _refund_client_deposit(self, deal: Deal):
        client_address = deal.get_data()['client_address']
        client_deposit = deal.get_data()['client_deposit']
        self.balance -= client_deposit
        self.balances[client_address] += client_deposit

    def post_client_payment(self, result: Result, tx: Tx):
        result_data = result.get_data()
        result_instruction_count = result_data['instruction_count']
        result_instruction_count = float(result_instruction_count)
        deal_id = result_data['deal_id']
        deal_data = self.deals[deal_id].get_data()
        price_per_instruction = deal_data['price_per_instruction']
        expected_payment_value = result_instruction_count * price_per_instruction
        if tx.value != expected_payment_value:
            print(f'transaction value of {tx.value} does not match expected payment value {expected_payment_value}')
            raise Exception("transaction value does not match expected payment value")
        client_address = deal_data['client_address']
        if expected_payment_value > self.balances[client_address]:
            print()
            print(f'transaction value of {tx.value} exceeds client balance of {self.balances[client_address]}')
            raise Exception("transaction value exceeds balance")
        # subtract from client's deposit
        self.balances[client_address] -= tx.value
        # add transaction value to smart contract balance
        self.balance += tx.value
        deal = self.deals[deal_id]
        resource_provider_address = deal.get_data()['resource_provider_address']
        # pay resource provider
        self.balances[resource_provider_address] += tx.value
        # subtract from smart contract balance
        self.balance -= tx.value
        # refund client deposit
        self._refund_client_deposit(deal)

    def fund(self, tx: Tx):
        self.balances[tx.sender] = self.balances.get(tx.sender, 0) + tx.value

    def _log_balances(self):
        self.logger.info(f"Smart Contract balance: {self.balance}")
        self.logger.info(f"Smart Contract balances: {self.balances}")

    def _get_balances(self):
        return self.balances

    def _get_balance(self):
        return self.balance

    def _smart_contract_loop(self):
        for match in self.matches_made_in_current_step:
            self._create_deal(match)
        self._create_and_emit_result_events()
        self._account_for_cheating_collateral_payments()
        self.matches_made_in_current_step.clear()
        self.results_posted_in_current_step.clear()
        self._log_balances()

