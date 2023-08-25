from utils import *
from service_provider import ServiceProvider
from service_provider_local_information import LocalInformation
from collections import deque
from job import Job
from solver import Solver
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

    def get_solver(self):
        return self.solver

    def get_smart_contract(self):
        return self.smart_contract

    def connect_to_solver(self, url: str, solver: Solver):
        self.solver_url = url
        self.solver = solver
        solver.subscribe_event(self.handle_solver_event)

    def connect_to_smart_contract(self, smart_contract: SmartContract):
        self.smart_contract = smart_contract
        smart_contract.subscribe_event(self.handle_smart_contract_event)

    def add_job(self, job: Job):
        self.current_jobs.append(job)

    def get_jobs(self):
        return self.current_jobs

    def handle_solver_event(self, event):
        self.logger.info(f"have solver event {event.get_name(), event.get_data().get_id()}")
        if event.get_name() == 'match':
            match = event.get_data()
            if match.get_data()['client_address'] == self.get_public_key():
                client_deposit = match.get_data()['client_deposit']
                tx = Tx(sender=self.get_public_key(), value=client_deposit)
                self.get_smart_contract().agree_to_match(match, tx)

    def handle_smart_contract_event(self, event):
        self.logger.info(f"have smart contract event {event.get_name(), event.get_data().get_id()}")
        if event.get_name() == 'deal':
            deal = event.get_data()
            deal_data = deal.get_data()
            deal_id = deal.get_id()
            if deal_data['client_address'] == self.get_public_key():
                self.current_deals[deal_id] = deal

        if event.get_name() == 'result':
            result = event.get_data()
            result_data = result.get_data()
            result_instruction_count = result_data['instruction_count']
            result_instruction_count = float(result_instruction_count)
            deal_id = result_data['deal_id']
            price_per_instruction = self.current_deals[deal_id].get_data()['price_per_instruction']
            payment_value = result_instruction_count * price_per_instruction
            tx = Tx(sender=self.get_public_key(), value=payment_value)
            self.smart_contract.post_client_payment(result, tx)
            self.deals_finished_in_current_step.append(deal_id)

    def update_finished_deals(self):
        # remove finished deals from list of current deals and running jobs
        for deal_id in self.deals_finished_in_current_step:
            del self.current_deals[deal_id]
        # clear list of deals finished in current step
        self.deals_finished_in_current_step.clear()
