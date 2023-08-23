from service_provider import ServiceProvider
from event import Event
from match import Match
from utils import *


class SmartContract(ServiceProvider):
    def __init__(self, public_key: str):
        super().__init__(public_key)
        self.transactions = []

    def agree_to_match(self, match: Match, tx: Tx):
        pass

    def _create_deal(self):
        pass

    def post_result(self):
        pass

    def fund(self, tx: Tx):
        pass
