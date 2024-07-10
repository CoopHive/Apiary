from utils import *
from machine import Machine
from service_provider import ServiceProvider
from solver import Solver
from match import Match
from smart_contract import SmartContract
from result import Result
import docker
import time
from datetime import datetime
import logging
# JSON Logging
from log_json import log_json
import os


class ResourceProvider(ServiceProvider):
    def __init__(self, public_key: str):
        # machines maps CIDs -> machine metadata
        super().__init__(public_key)
        self.logger = logging.getLogger(f"Resource Provider {self.public_key}")
        logging.basicConfig(filename=f'{os.getcwd()}/local_logs', filemode='w', level=logging.DEBUG)
        self.machines = {}
        self.solver_url = None
        self.solver = None
        self.smart_contract = None
        self.current_deals = {}  # maps deal id to deals
        # changed to simulate running a docker job
        self.current_jobs = {}
        self.docker_client = docker.from_env()
        #self.current_job_running_times = {}  # maps deal id to how long the resource provider has been running the job
        self.deals_finished_in_current_step = []
        self.current_matched_offers = []

        self.docker_username = 'your_dockerhub_username'
        self.docker_password = 'your_dockerhub_password'

        self.login_to_docker()
    
    def login_to_docker(self):
        try:
            self.docker_client.login(username=self.docker_username, password=self.docker_password)
            self.logger.info("Logged into Docker Hub successfully")
        except docker.errors.APIError as e:
            self.logger.error(f"Failed to log into Docker Hub: {e}")

    def get_solver(self):
        return self.solver

    def get_smart_contract(self):
        return self.smart_contract

    def connect_to_solver(self, url: str, solver: Solver):
        self.solver_url = url
        self.solver = solver
        self.solver.subscribe_event(self.handle_solver_event)
        self.solver.get_local_information().add_resource_provider(self)
        # JSON logging
        log_json(self.logger, "Connected to solver", {"solver_url": url})

    def connect_to_smart_contract(self, smart_contract: SmartContract):
        self.smart_contract = smart_contract
        smart_contract.subscribe_event(self.handle_smart_contract_event)
        # JSON logging
        log_json(self.logger, "Connected to smart contract")

    def add_machine(self, machine_id: CID, machine: Machine):
        self.machines[machine_id.hash] = machine

    def remove_machine(self, machine_id):
        self.machines.pop(machine_id)

    def get_machines(self):
        return self.machines

    def create_resource_offer(self):
        pass

    def _agree_to_match(self, match: Match):
        timeout_deposit = match.get_data()['timeout_deposit']
        tx = self._create_transaction(timeout_deposit)
        #tx = Tx(sender=self.get_public_key(), value=timeout_deposit)
        self.get_smart_contract().agree_to_match(match, tx)
        # JSON logging
        log_json(self.logger, "Agreed to match", {"match_id": match.get_id()})


    def handle_solver_event(self, event):
        # JSON logging
        event_data = {"name": event.get_name(), "id": event.get_data().get_id()}
        log_json(self.logger, "Received solver event", {"event_data": event_data})

        #self.logger.info(f"have solver event {event.get_name(), event.get_data().get_id()}")
        if event.get_name() == 'match':
            match = event.get_data()
            if match.get_data()['resource_provider_address'] == self.get_public_key():
                self.current_matched_offers.append(match)

    def handle_smart_contract_event(self, event):
        if event.get_name() == 'mediation_random':
            #JSON logging
            event_data = {"name": event.get_name(), "id": event.get_data().get_id()}
            log_json(self.logger, "Received smart contract event", {"event_data": event_data})
            #self.logger.info(f"have smart contract event {event.get_name()}")        
        elif event.get_name() == 'deal':
            #JSON logging
            event_data = {"name": event.get_name(), "id": event.get_data().get_id()}
            log_json(self.logger, "Received smart contract event", {"event_data": event_data})
            #self.logger.info(f"have smart contract event {event.get_name(), event.get_data().get_id()}")
            deal = event.get_data()
            deal_data = deal.get_data()
            deal_id = deal.get_id()
            if deal_data['resource_provider_address'] == self.get_public_key():
                self.current_deals[deal_id] = deal
                # changed to simulate running a docker job
                container = self.docker_client.containers.run("alpine", "sleep 30", detach=True)
                self.current_jobs[deal_id] = container
                #self.current_job_running_times[deal_id] = 0

    def post_result(self, result: Result, tx: Tx):
        self.get_smart_contract().post_result(result, tx)

    def create_result(self, deal_id):
        # JSON logging
        result_log_data = {"deal_id": deal_id}
        log_json(self.logger, "Creating result", result_log_data)
        #self.logger.info(f"posting the result for deal {deal_id}")
        result = Result()
        result.add_data('deal_id', deal_id)
        instruction_count = 1
        result.add_data('instruction_count', instruction_count)
        result.set_id()
        result.add_data('result_id', result.get_id())
        cheating_collateral_multiplier = self.current_deals[deal_id].get_data()['cheating_collateral_multiplier']
        cheating_collateral = cheating_collateral_multiplier * int(instruction_count)
        tx = self._create_transaction(cheating_collateral)
        #tx = Tx(sender=self.get_public_key(), value=cheating_collateral)
        return result, tx

    def update_finished_deals(self):
        # remove finished deals from list of current deals and running jobs
        for deal_id in self.deals_finished_in_current_step:
            del self.current_deals[deal_id]
            # changed to simulate running a docker job
            del self.current_jobs[deal_id]
        # clear list of deals finished in current step
        self.deals_finished_in_current_step.clear()

    def handle_completed_job(self, deal_id):
        # added to simulate running a docker job
        container = self.current_jobs[deal_id]
        container.stop()
        container.remove()
        result, tx = self.create_result(deal_id)
        self.post_result(result, tx)
        self.deals_finished_in_current_step.append(deal_id)

    def update_job_running_times(self):
        # changed to simulate running a docker job
        for deal_id, container in self.current_jobs.items():
            container.reload()
            if container.status == "exited":
                self.handle_completed_job(deal_id)
        self.update_finished_deals()

    def resource_provider_loop(self):
        for match in self.current_matched_offers:
            self._agree_to_match(match)
        self.update_job_running_times()
        self.current_matched_offers.clear()


# todo when handling events, add to list to be managed later, i.e. don't start signing stuff immediately













