from service_provider import ServiceProvider
from event import Event
from match import Match
from utils import *


class SmartContract(ServiceProvider):
    def __init__(self, public_key: str):
        super().__init__(public_key)
        self.transactions = []

    def agree_to_match(self, match: Match, tx: Tx):
        if match.get_data()['resource_provider_address'] == tx.sender:
            match.sign_resource_provider()
            print('rp hit')
        elif match.get_data()['client_address'] == tx.sender:
            match.sign_client()
            print('client hit')
        if match.get_resource_provider_signed() and match.get_client_signed():
            print('both rp and client have signed')

    def _create_deal(self):
        pass

    def post_result(self):
        pass

    def fund(self, tx: Tx):
        pass
