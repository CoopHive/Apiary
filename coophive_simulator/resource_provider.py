"""Module for defining the ResourceProvider class and its related functionalities."""

import logging
import os

import docker

from coophive_simulator.log_json import log_json
from coophive_simulator.machine import Machine
from coophive_simulator.match import Match
from coophive_simulator.result import Result
from coophive_simulator.service_provider import ServiceProvider
from coophive_simulator.smart_contract import SmartContract
from coophive_simulator.solver import Solver
from coophive_simulator.utils import *


# TODO: centralize logging settings and initialization at the initial setup of the package functionality calls.
class ResourceProvider(ServiceProvider):
    """Class representing a resource provider in the CoopHive simulator.

    Attributes:
        public_key (str): The public key associated with the resource provider.
        logger (logging.Logger): Logger instance for logging resource provider events.
        machines (dict): Dictionary mapping machine IDs to machine metadata.
        solver_url (str): URL of the connected solver.
        solver (Solver): Instance of the connected solver.
        smart_contract (SmartContract): Instance of the connected smart contract.
        current_deals (dict): Dictionary mapping deal IDs to deals.
        current_jobs (dict): Dictionary mapping deal IDs to running jobs.
        docker_client (docker.client.DockerClient): Docker client instance.
        deals_finished_in_current_step (list): List of deal IDs finished in the current simulation step.
        current_matched_offers (list): List of currently matched offers.
        docker_username (str): Docker Hub username.
        docker_password (str): Docker Hub password.
    """

    def __init__(self, public_key: str):
        """Initialize the ResourceProvider instance.

        Args:
            public_key (str): The public key associated with the resource provider.
        """

        # machines maps CIDs -> machine metadata
        super().__init__(public_key)
        self.logger = logging.getLogger(f"Resource Provider {self.public_key}")
        logging.basicConfig(
            filename=f"{os.getcwd()}/local_logs", filemode="w", level=logging.DEBUG
        )
        self.machines = {}
        self.solver_url = None
        self.solver = None
        self.smart_contract = None
        self.current_deals = {}  # maps deal id to deals
        # changed to simulate running a docker job
        self.current_jobs = {}
        self.docker_client = docker.from_env()
        # self.current_job_running_times = {}  # maps deal id to how long the resource provider has been running the job
        self.deals_finished_in_current_step = []
        self.current_matched_offers = []

        self.docker_username = "your_dockerhub_username"
        self.docker_password = "your_dockerhub_password"

        self.login_to_docker()

    def login_to_docker(self):
        """Log in to Docker Hub using the provided username and password."""
        try:
            self.docker_client.login(
                username=self.docker_username, password=self.docker_password
            )
            self.logger.info("Logged into Docker Hub successfully")
        except docker.errors.APIError as e:
            self.logger.error(f"Failed to log into Docker Hub: {e}")

    def get_solver(self):
        """Get the connected solver instance."""
        return self.solver

    def get_smart_contract(self):
        """Get the connected smart contract instance."""
        return self.smart_contract

    def connect_to_solver(self, url: str, solver: Solver):
        """Connect to a solver with the provided URL and solver instance.

        Args:
            url (str): The URL of the solver.
            solver (Solver): The solver instance to connect to.
        """
        self.solver_url = url
        self.solver = solver
        self.solver.subscribe_event(self.handle_solver_event)
        self.solver.get_local_information().add_resource_provider(self)
        log_json(self.logger, "Connected to solver", {"solver_url": url})

    def connect_to_smart_contract(self, smart_contract: SmartContract):
        """Connect to a smart contract with the provided instance.

        Args:
            smart_contract (SmartContract): The smart contract instance to connect to.
        """
        self.smart_contract = smart_contract
        smart_contract.subscribe_event(self.handle_smart_contract_event)

        log_json(self.logger, "Connected to smart contract")

    def add_machine(self, machine_id: CID, machine: Machine):
        """Add a machine to the resource provider.

        Args:
            machine_id (CID): The ID of the machine to add.
            machine (Machine): The machine instance to add.
        """
        self.machines[machine_id.hash] = machine

    def remove_machine(self, machine_id):
        """Remove a machine from the resource provider.

        Args:
            machine_id: The ID of the machine to remove.
        """
        self.machines.pop(machine_id)

    def get_machines(self):
        """Get all machines associated with the resource provider.

        Returns:
            dict: Dictionary mapping machine IDs to machine instances.
        """
        return self.machines

    def create_resource_offer(self):
        """Placeholder for resource offer creation."""
        pass

    def _agree_to_match(self, match: Match):
        """Agree to a match and send a transaction to the connected smart contract.

        Args:
            match (Match): The match instance to agree to.
        """
        timeout_deposit = match.get_data()["timeout_deposit"]
        tx = self._create_transaction(timeout_deposit)
        self.get_smart_contract().agree_to_match(match, tx)
        log_json(self.logger, "Agreed to match", {"match_id": match.get_id()})

    def handle_solver_event(self, event):
        """Handle events received from the connected solver.

        Args:
            event: The event object received from the solver.
        """
        event_data = {"name": event.get_name(), "id": event.get_data().get_id()}
        log_json(self.logger, "Received solver event", {"event_data": event_data})

        if event.get_name() == "match":
            match = event.get_data()
            if match.get_data()["resource_provider_address"] == self.get_public_key():
                self.current_matched_offers.append(match)

    def handle_smart_contract_event(self, event):
        """Handle events received from the connected smart contract.

        Args:
            event: The event object received from the smart contract.
        """
        if event.get_name() == "mediation_random":

            event_data = {"name": event.get_name(), "id": event.get_data().get_id()}
            log_json(
                self.logger, "Received smart contract event", {"event_data": event_data}
            )
        elif event.get_name() == "deal":
            event_data = {"name": event.get_name(), "id": event.get_data().get_id()}
            log_json(
                self.logger, "Received smart contract event", {"event_data": event_data}
            )
            deal = event.get_data()
            deal_data = deal.get_data()
            deal_id = deal.get_id()
            if deal_data["resource_provider_address"] == self.get_public_key():
                self.current_deals[deal_id] = deal
                # changed to simulate running a docker job
                container = self.docker_client.containers.run(
                    "alpine", "sleep 30", detach=True
                )
                self.current_jobs[deal_id] = container
                # self.current_job_running_times[deal_id] = 0

    def post_result(self, result: Result, tx: Tx):
        """Post a result to the connected smart contract.

        Args:
            result (Result): The result object to post.
            tx (Tx): The transaction metadata associated with the posting.
        """
        self.get_smart_contract().post_result(result, tx)

    def create_result(self, deal_id):
        """Create a result for the specified deal ID.

        Args:
            deal_id: The ID of the deal for which to create the result.

        Returns:
            Tuple[Result, Tx]: The created result object and associated transaction metadata.
        """
        result_log_data = {"deal_id": deal_id}
        log_json(self.logger, "Creating result", result_log_data)
        result = Result()
        result.add_data("deal_id", deal_id)
        instruction_count = 1
        result.add_data("instruction_count", instruction_count)
        result.set_id()
        result.add_data("result_id", result.get_id())
        cheating_collateral_multiplier = self.current_deals[deal_id].get_data()[
            "cheating_collateral_multiplier"
        ]
        cheating_collateral = cheating_collateral_multiplier * int(instruction_count)
        tx = self._create_transaction(cheating_collateral)
        return result, tx

    def update_finished_deals(self):
        """Update the list of finished deals by removing them from the current deals and jobs lists."""
        # remove finished deals from list of current deals and running jobs
        for deal_id in self.deals_finished_in_current_step:
            del self.current_deals[deal_id]
            # changed to simulate running a docker job
            del self.current_jobs[deal_id]
        # clear list of deals finished in current step
        self.deals_finished_in_current_step.clear()

    def handle_completed_job(self, deal_id):
        """Handle completion of a job associated with a deal.

        Args:
            deal_id: The ID of the deal whose job has completed.
        """
        # added to simulate running a docker job
        container = self.current_jobs[deal_id]
        container.stop()
        container.remove()
        result, tx = self.create_result(deal_id)
        self.post_result(result, tx)
        self.deals_finished_in_current_step.append(deal_id)

    def update_job_running_times(self):
        """Update the running times of current jobs and handle completed jobs."""
        # changed to simulate running a docker job
        for deal_id, container in self.current_jobs.items():
            container.reload()
            if container.status == "exited":
                self.handle_completed_job(deal_id)
        self.update_finished_deals()

    def resource_provider_loop(self):
        """Main loop for the resource provider to process matched offers and update job running times."""
        for match in self.current_matched_offers:
            self._agree_to_match(match)
        self.update_job_running_times()
        self.current_matched_offers.clear()


# TODO: when handling events, add to list to be managed later, i.e. don't start signing stuff immediately
