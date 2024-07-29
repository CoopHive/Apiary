"""Module for defining the ResourceProvider class and its related functionalities."""

import logging
import os
import socket
import threading
import time

import docker

from coophive_simulator.globals import global_time
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
    """Class representing a resource provider in the CoopHive simulator."""

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
        self.current_jobs = {}
        self.docker_client = docker.from_env()
        self.deals_finished_in_current_step = []
        self.current_matched_offers = []
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
        logging.info("Server listening on port 1234")
        threading.Thread(target=self.accept_clients, daemon=True).start()

    def accept_clients(self):
        """Continuously accepts incoming client connections. For each new connection, a new thread is spawned to handle the client's messages."""
        while True:
            client_socket, addr = self.server_socket.accept()
            logging.info(f"Connection established with {addr}")
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
                message = message.decode(
                    "utf-8"
                )  # Decode the message from bytes to string
                logging.info(f"Received message from client: {message}")
                match_data = eval(
                    message.split("New match offer: ")[1]
                )  # Convert string to dictionary
                match = Match(match_data)
                response = self.evaluate_match(match)
                client_socket.send(response.encode("utf-8"))
            except ConnectionResetError:
                logging.info("Connection lost. Closing connection.")
                client_socket.close()
                break
            except Exception as e:
                logging.info(f"Error handling message: {e}")

    def evaluate_match(self, match):
        """Here you evaluate the match and decide whether to accept or counteroffer."""
        if self.calculate_utility(match) > match.get_data()["T_accept"]:
            return "accepted"
        else:
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

    # TODO: Implement this function
    def handle_p2p_event(self, event):
        """P2P handling.

        if the resource provider hears about a job_offer, it should check if its an appropriate match the way handle_solver_event
        determines that a match exists (if all required machine keys (CPU, RAM) have exactly the same values in both the job offer
        and the resource offer) -> then create a match and append to current_matched_offers.
        """
        pass

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

    def make_match_decision(self, match, algorithm):
        """Make a decision on a match based on the specified algorithm.

        Args:
            match: The match instance to make a decision on.
            algorithm (str): The algorithm to use for making the decision. Can be "accept_all", "accept_reject", or "accept_reject_negotiate".
        """
        if algorithm == "accept_all":
            self._agree_to_match(match)
        elif algorithm == "accept_reject":
            match_utility = self.calculate_utility(match)

            best_match = self.find_best_match_for_resource_offer(
                match.get_data()["resource_offer"]
            )
            # could also check that match_utility > self.T_reject to make it more flexible (basically accept a match if its utility is over T_reject instead of over T_accept)

            # TODO: update where T_accept is accessed from if its moved to resource_offer
            if best_match == match and match_utility > match.get_data()["T_accept"]:
                self._agree_to_match(match)
            else:
                self.reject_match(match)
        elif algorithm == "accept_reject_negotiate":
            #   Negotiate if the utility is within range of being acceptable (between T_reject and T_accept). Call some function negotiate_match
            #   that takes the match as an input and creates a similar but new match where the utility of the new match is > T_accept.
            #                   Should be able to handle multiple negotiation rounds.
            #                   IMPLEMENT NEGOTIATIONS OVER HTTP: Parameter for how many rounds until negotiation ends (ex: 5).
            best_match = self.find_best_match_for_resource_offer(
                match.get_data()["resource_offer"]
            )
            if best_match == match:
                utility = self.calculate_utility(match)
                # TODO: update where T_accept is accessed from if its moved to resource_offer
                if utility > match.get_data()["T_accept"]:
                    self._agree_to_match(match)
                # TODO: update where T_reject is accessed from if its moved to resource_offer
                elif utility < match.get_data()["T_reject"]:
                    self.reject_match(match)
                else:
                    self.negotiate_match(match)
            else:
                self.reject_match(match)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        # Other considerations:
        #   Check whether there is already a deal in progress for the current resource offer, if yes, reject this match.
        #   Introduce a flexibility factor that allows flexibility for when a cient decides to negotiate or reject (manipulates T_reject or utility somehow).
        #       - It allows for some degree of negotiation, making the client less rigid and more adaptable to market conditions.
        #   T_accept and T_reject may be static or dynamically adjusted based on historical data or current market conditions.

    def find_best_match_for_resource_offer(self, resource_offer_id):
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

    # Currently T_accept is -15 and T_reject to -30 but that DEFINITELY needs to be changed
    # NOTE: this utility calculation is DIFFERENT for a resource provider than for a client
    def calculate_utility(self, match):
        """Calculate the utility of a match based on several factors.

        COST and TIME are the main determiners.
        """
        expected_revenue = self.calculate_revenue(match)
        return expected_revenue

    # TODO: Implement rejection logic. If a client or compute node rejects a match, it needs to be offered that match again
    # (either via the solver or p2p negotiation) in order to accept it.
    def reject_match(self, match):
        """Reject the given match."""
        log_json(self.logger, "Rejected match", {"match_id": match.get_id()})
        pass

    # TODO: Implement negotiation logic. Implement HTTP communication for negotiation
    def negotiate_match(self, match, max_rounds=5):
        """Negotiate the given match."""
        log_json(self.logger, "Negotiating match", {"match_id": match.get_id()})
        for _ in range(max_rounds):
            new_match_offer = self.create_new_match_offer(match)
            response = self.communicate_request_to_party(
                match.get_data()["client_address"], new_match_offer
            )
            if response["accepted"]:
                self._agree_to_match(response["match"])
                return
            match = response["counter_offer"]
        self.reject_match(match)

    def create_new_match_offer(self, match):
        """Create a new match offer by modifying the price per instruction.

        Args:
            match (Match): The match object to base the new offer on.

        Returns:
            Match: A new match object with the updated price.
        """
        data = match.get_data()
        new_data = data.copy()
        new_data["price_per_instruction"] = (
            data["price_per_instruction"] * 1.05
        )  # For example, increase the price
        new_data["T_accept"] = data.get(
            "T_accept", -10
        )  # Default value if T_accept is not present
        new_data["T_reject"] = data.get(
            "T_reject", -20
        )  # Default value if T_reject is not present
        new_match = Match(new_data)
        return new_match

    def communicate_request_to_party(self, party_id, match_offer):
        """Communicate a match offer to a specified party and return the response.

        Args:
            party_id (str): The ID of the party to communicate with.
            match_offer (Match): The match offer to be communicated.

        Returns:
            dict: The response from the party.
        """
        # Simulate communication - this would need to be implemented with actual P2P or HTTP communication
        log_json(
            self.logger,
            "Communicating request to party",
            {"party_id": party_id, "match_offer": match_offer.get_data()},
        )
        response = self.simulate_communication(party_id, match_offer)
        return response

    def simulate_communication(self, party_id, match_offer):
        """Simulate communication with a party to get their response to a match offer.

        Args:
            party_id (str): The ID of the party to communicate with.
            match_offer (Match): The match offer being sent.

        Returns:
            dict: A simulated response from the party, including whether the offer was accepted or a counter-offer.
        """
        message = f"New match offer: {match_offer.get_data()}"
        self.client_socket.send(message.encode("utf-8"))
        response_message = self.client_socket.recv(1024).decode("utf-8")
        log_json(
            self.logger,
            "Received response from server",
            {"response_message": response_message},
        )

        response = {
            "accepted": "accepted" in response_message,
            "counter_offer": self.create_new_match_offer(match_offer),
        }
        return response

    def resource_provider_loop(self):
        """Main loop for the resource provider to process matched offers and update job running times."""
        for match in self.current_matched_offers:
            self.make_match_decision(match, algorithm="accept_reject_negotiate")
        self.update_job_running_times()
        self.current_matched_offers.clear()


# TODO: when handling events, add to list to be managed later, i.e. don't start signing stuff immediately

if __name__ == "__main__":
    public_key = "Your public key here"  # Replace with the actual public key
    resource_provider = ResourceProvider(public_key)
    resource_provider.resource_provider_loop()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Server shutting down.")
