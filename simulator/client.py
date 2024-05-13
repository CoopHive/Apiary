from utils import *
from service_provider import ServiceProvider
from service_provider_local_information import LocalInformation
from collections import deque
from job import Job
from solver import Solver
from match import Match
from smart_contract import SmartContract
import logging
import os


class Client(ServiceProvider):
    def __init__(self, address: str):
        super().__init__(address)
        self.logger = logging.getLogger(f"Client {self.public_key}")
        logging.basicConfig(filename=f'{os.getcwd()}/local_logs', filemode='w', level=logging.DEBUG)
        # TODO: should determine the best data structure for this
        self.current_jobs = deque()
        self.local_information = LocalInformation()
        self.solver_url = None
        self.solver = None
        self.current_deals = {}  # maps deal id to deals
        self.deals_finished_in_current_step = []
        self.current_matched_offers = []

    def get_solver(self):
        return self.solver

    def get_smart_contract(self):
        return self.smart_contract

    def connect_to_solver(self, url: str, solver: Solver):
        self.solver_url = url
        self.solver = solver
        self.solver.subscribe_event(self.handle_solver_event)
        self.solver.get_local_information().add_client(self)

    def connect_to_smart_contract(self, smart_contract: SmartContract):
        self.smart_contract = smart_contract
        smart_contract.subscribe_event(self.handle_smart_contract_event)

    def add_job(self, job: Job):
        self.current_jobs.append(job)

    def get_jobs(self):
        return self.current_jobs

    def _agree_to_match(self, match: Match):
        client_deposit = match.get_data()['client_deposit']
        tx = Tx(sender=self.get_public_key(), value=client_deposit)
        self.get_smart_contract().agree_to_match(match, tx)

    def handle_solver_event(self, event):
        self.logger.info(f"have solver event {event.get_name(), event.get_data().get_id()}")
        if event.get_name() == 'match':
            match = event.get_data()
            if match.get_data()['client_address'] == self.get_public_key():
                self.current_matched_offers.append(match)

    def decide_whether_or_not_to_mediate(self, event):
        # for now, always mediate
        return True
        
    def request_mediation(self, event):        
        self.logger.info(f"requesting mediation {event.get_name()}")
        self.smart_contract.mediate_result(event)

    def pay_compute_node(self, event):
        result = event.get_data()
        result_data = result.get_data()
        deal_id = result_data['deal_id']
        if deal_id in self.current_deals.keys():
            result_instruction_count = result_data['instruction_count']
            result_instruction_count = float(result_instruction_count)
            price_per_instruction = self.current_deals[deal_id].get_data()['price_per_instruction']
            payment_value = result_instruction_count * price_per_instruction
            tx = Tx(sender=self.get_public_key(), value=payment_value)
            self.smart_contract.post_client_payment(result, tx)
            self.deals_finished_in_current_step.append(deal_id)
    
    def handle_smart_contract_event(self, event):
        if event.get_name() == 'mediation_random':
            self.logger.info(f"have smart contract event {event.get_name()}")        
        if event.get_name() == 'deal':
            self.logger.info(f"have smart contract event {event.get_name(), event.get_data().get_id()}")
            deal = event.get_data()
            deal_data = deal.get_data()
            deal_id = deal.get_id()
            if deal_data['client_address'] == self.get_public_key():
                self.current_deals[deal_id] = deal

        if event.get_name() == 'result':
            # decide whether to mediate result
            mediate_flag = self.decide_whether_or_not_to_mediate(event)
            if mediate_flag:
                mediation_result = self.request_mediation(event)
                """
                mediation should be handled automatically by the smart contract
                in fact, shouldn't the payment also be handled automatically by the smart contract?
                """
            # if not requesting mediation, send payment to compute node
            else:
                self.pay_compute_node(event)

    def update_finished_deals(self):
        # remove finished deals from list of current deals and running jobs
        for deal_id in self.deals_finished_in_current_step:
            del self.current_deals[deal_id]
        # clear list of deals finished in current step
        self.deals_finished_in_current_step.clear()

    def client_loop(self):
        for match in self.current_matched_offers:
            self._agree_to_match(match)
        self.update_finished_deals()
        self.current_matched_offers.clear()

