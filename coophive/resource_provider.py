"""Module for defining the ResourceProvider class and its related functionalities."""

import socket
import threading

import docker

from coophive.agent import Agent
from coophive.log_json import log_json
from coophive.match import Match
from coophive.policy import Policy
from coophive.result import Result
from coophive.utils import Tx


class ResourceProvider(Agent):
    """Class representing a resource provider in the CoopHive simulator."""

    def __init__(
        self,
        private_key: str,
        public_key: str,
        policy: Policy,
        auxiliary_states: dict = {},
    ):
        """Initialize the ResourceProvider instance."""
        super().__init__(
            private_key=private_key,
            public_key=public_key,
            policy=policy,
            auxiliary_states=auxiliary_states,
        )
        self.machines = {}
        self.docker_client = docker.from_env()
        self.server_socket = None
        self.start_server_socket()
        self.docker_username = "your_dockerhub_username"
        self.docker_password = "your_dockerhub_password"
        self.login_to_docker()

    def start_server_socket(self):
        """Initializes the server socket, binds it to a local address and port, and starts listening for incoming connections."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("localhost", 1234))
        self.server_socket.listen(5)
        self.logger.info("Server listening on port 1234")
        threading.Thread(target=self.accept_clients, daemon=True).start()

    def accept_clients(self):
        """Continuously accepts incoming client connections. For each new connection, a new thread is spawned to handle the client's messages."""
        while True:
            client_socket, addr = self.server_socket.accept()
            self.logger.info(f"Connection established with {addr}")
            threading.Thread(
                target=self.handle_client_messages, args=(client_socket,), daemon=True
            ).start()

    def handle_client_messages(self, client_socket):
        """Handles incoming messages from a connected client."""
        while True:
            try:
                message = client_socket.recv(1024)
                if not message:
                    break
                # Decode the message from bytes to string
                message = message.decode("utf-8")
                self.logger.info(f"Received message from client: {message}")
                if "New match offer" in message:
                    match_data = eval(message.split("New match offer: ")[1])
                    match = Match(match_data)
                    match_dict = match.get_data()
                    if "rounds_completed" not in match_dict:
                        match.rounds_completed = 0
                    # Check if the match is already in current_matched_offers by ID
                    for existing_match in self.current_matched_offers:
                        if existing_match.get_id() == match.get_id():
                            # Continue negotiating on the existing match
                            self.negotiate_match(existing_match)
                            break
                    else:
                        # New match, add to current_matched_offers and process
                        self.current_matched_offers.append(match)
                        response = self.make_match_decision(match)
                        client_socket.send(response.encode("utf-8"))
            except ConnectionResetError:
                self.logger.info("Connection lost. Closing connection.")
                client_socket.close()
                break
            except Exception as e:
                self.logger.info(f"Error handling message: {e}")

    # TODO: transfer functionality inside policy evaluation at the agent level.
    def evaluate_match(self, match):
        """Here you evaluate the match and decide whether to accept or counteroffer."""
        if (
            self.calculate_utility(match)
            > match.get_data()["resource_offer"]["T_accept"]
        ):
            return "RP accepted from evaluate match"
        elif (
            self.calculate_utility(match)
            < match.get_data()["resource_offer"]["T_reject"]
        ):
            return "RP rejected from evaluate match"
        else:
            self.logger.info("RP sending counteroffer from evaluate match")
            counter_offer = self.create_new_match_offer(match)
            return f"New match offer: {counter_offer.get_data()}"

    def login_to_docker(self):
        """Log in to Docker Hub using the provided username and password."""
        try:
            self.docker_client.login(
                username=self.docker_username, password=self.docker_password
            )
            log_json(self.logger, "Logged into Docker Hub successfully")
        except docker.errors.APIError as e:
            log_json(self.logger, f"Failed to log into Docker Hub: {e}")

    def _agree_to_match(self, match: Match):
        """Agree to a match and send a transaction to the connected smart contract.

        Args:
            match (Match): The match instance to agree to.
        """
        timeout_deposit = match.get_data()["timeout_deposit"]
        tx = self._create_transaction(timeout_deposit)
        self.get_smart_contract().agree_to_match(match, tx)
        log_json(self.logger, "Agreed to match", {"match_id": match.get_id()})

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
        log_json(self.logger, "Posted result", {"result_id": result.get_id()})

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
        # Call the superclass method to handle the common logic
        super().update_finished_deals()

        # Additional subclass-specific logic
        for deal_id in self.deals_finished_in_current_step:
            del self.current_jobs[deal_id]

    def handle_completed_job(self, deal_id):
        """Handle completion of a job associated with a deal.

        Args:
            deal_id: The ID of the deal whose job has completed.
        """
        container = self.current_jobs[deal_id]
        container.stop()
        container.remove()
        result, tx = self.create_result(deal_id)
        self.post_result(result, tx)
        self.deals_finished_in_current_step.append(deal_id)

    def update_job_running_times(self):
        """Update the running times of current jobs and handle completed jobs."""
        for deal_id, container in self.current_jobs.items():
            container.reload()
            if container.status == "exited":
                self.handle_completed_job(deal_id)
        self.update_finished_deals()

    # TODO: transfer functionality inside policy evaluation at the agent level.
    def find_best_match(self, resource_offer_id):
        """Find the best match for a given resource offer based on utility.

        Args:
            resource_offer_id: The ID of the resource offer.

        Returns:
            match: The match with the highest utility for the given resource offer.
        """
        best_match = None
        highest_utility = -float("inf")
        for match in self.current_matched_offers:
            if match.get_data()["resource_offer"] == resource_offer_id:
                utility = self.calculate_utility(match)
                if utility > highest_utility:
                    highest_utility = utility
                    best_match = match
        return best_match

    # TODO: transfer functionality inside policy evaluation at the agent level.
    def calculate_revenue(self, match):
        """Calculate the revenue generated from a match.

        Args:
            match: An object containing the match details.

        Returns:
            float: The revenue from the match based on some calculation.
        """
        data = match.get_data()
        price_per_instruction = data.get("price_per_instruction", 0)
        expected_number_of_instructions = data.get("expected_number_of_instructions", 0)
        return price_per_instruction * expected_number_of_instructions

    # TODO: transfer functionality inside policy evaluation at the agent level.
    # NOTE: this utility calculation is DIFFERENT for a resource provider than for a client
    def calculate_utility(self, match):
        """Calculate the utility of a match based on several factors.

        COST and TIME are the main determiners.
        """
        expected_revenue = self.calculate_revenue(match)
        return expected_revenue

    def make_match_decision(self, match):
        """Make a decision on whether to accept, reject, or negotiate a match."""
        localInfo = self.get_local_information()
        decision, counter = self.policy.infer(match, localInfo)
        if decision == "accept":
            self._agree_to_match(match)
        elif decision == "reject":
            self.reject_match(match)
        elif decision == "negotiate":
            self.negotiate_match(match)
        else:
            raise ValueError(f"Unknown policy decision: {decision}")

    # TODO: move this functionality in the networking model, at the agent level
    def resource_provider_loop(self):
        """Main loop for the resource provider to process matched offers and update job running times."""
        for match in self.current_matched_offers:
            self.make_match_decision(match)
        self.update_job_running_times()
        self.current_matched_offers.clear()
