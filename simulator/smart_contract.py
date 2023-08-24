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

    def agree_to_match(self, match: Match, tx: Tx):
        if match.get_data()['resource_provider_address'] == tx.sender:
            match.sign_resource_provider()
            print('rp has signed')
        elif match.get_data()['client_address'] == tx.sender:
            match.sign_client()
            print('client has signed')
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

    def post_result(self, result: Result, tx: Tx):
        deal_id = result.get_data()['deal_id']
        if self.deals[deal_id].get_data()['resource_provider_address'] == tx.sender:
            result_event = Event(name='result', data=result)
            self.emit_event(result_event)

    def fund(self, tx: Tx):
        pass
