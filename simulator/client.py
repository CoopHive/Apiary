from utils import *
from service_provider import ServiceProvider
from service_provider_local_information import LocalInformation
from collections import deque
from job import Job
from solver import Solver
from smart_contract import SmartContract


class Client(ServiceProvider):
    def __init__(self, address: str):
        super().__init__(address)
        # TODO: should determine the best data structure for this
        self.current_jobs = deque()
        self.local_information = LocalInformation()
        self.solver_url = None
        self.solver = None

    def get_solver(self):
        return self.solver

    def connect_to_solver(self, url: str, solver: Solver):
        self.solver_url = url
        self.solver = solver
        solver.subscribe_event(self.handle_event)

    def connect_to_smart_contract(self, smart_contract: SmartContract):
        self.smart_contract = smart_contract
        smart_contract.subscribe_event(self.handle_smart_contract_event)

    def add_job(self, job: Job):
        self.current_jobs.append(job)

    def get_jobs(self):
        return self.current_jobs

    def handle_event(self, event):
        print(f"I, the Client have event {event.get_name(), event.get_data().get_id()}")
        if event.get_name() == 'match':
            match = event.get_data()
            if match.get_data()['client_address'] == self.get_public_key():
                tx = Tx(sender=self.get_public_key(), value=1)
                self.smart_contract.agree_to_match(match, tx)

    def handle_smart_contract_event(self, event):
        print(f"I, the Client have smart contract event {event.get_name(), event.get_data().get_id()}")

