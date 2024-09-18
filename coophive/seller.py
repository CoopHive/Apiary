"""Module for defining the Seller class and its related functionalities."""

import logging

from coophive.agent import Agent
from coophive.match import Match
from coophive.result import Result
from coophive.utils import Tx, log_json


class Seller(Agent):
    """Class representing a seller in the CoopHive protocol."""

    def __init__(
        self,
        private_key: str,
        public_key: str,
        policy_name: str,
    ):
        """Initialize the Seller instance."""
        super().__init__(
            private_key=private_key,
            public_key=public_key,
            policy_name=policy_name,
        )

    def handle_client_messages(self, client_socket):
        """Handles incoming messages from a connected client."""
        while True:
            try:
                message = client_socket.recv(1024)
                if not message:
                    break
                # Decode the message from bytes to string
                message = message.decode("utf-8")
                logging.info(f"Received message from client: {message}")
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
                logging.info("Connection lost. Closing connection.")
                client_socket.close()
                break
            except Exception as e:
                logging.info(f"Error handling message: {e}")

    def _agree_to_match(self, match: Match):
        """Agree to a match and send a transaction to the connected smart contract.

        Args:
            match (Match): The match instance to agree to.
        """
        timeout_deposit = match.get_data()["timeout_deposit"]
        tx = self._create_transaction(timeout_deposit)
        self.get_smart_contract().agree_to_match(match, tx)
        log_json("Agreed to match", {"match_id": match.get_id()})

    def handle_smart_contract_event(self, event):
        """Handle events received from the connected smart contract.

        Args:
            event: The event object received from the smart contract.
        """
        if event.name == "mediation_random":

            event_data = {"name": event.name, "id": event.get_data().get_id()}
            log_json("Received smart contract event", {"event_data": event_data})
        elif event.name == "deal":

            event_data = {"name": event.name, "id": event.get_data().get_id()}
            log_json("Received smart contract event", {"event_data": event_data})
            deal = event.get_data()
            deal_data = deal.get_data()
            deal_id = deal.get_id()
            if deal_data["seller_address"] == self.public_key:
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
        log_json("Posted result", {"result_id": result.get_id()})

    def create_result(self, deal_id):
        """Create a result for the specified deal ID.

        Args:
            deal_id: The ID of the deal for which to create the result.

        Returns:
            Tuple[Result, Tx]: The created result object and associated transaction metadata.
        """
        log_json("Creating result", {"deal_id": deal_id})
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

    # TODO: move this functionality in the networking model, at the agent level
    def seller_loop(self):
        """Main loop for the seller to process matched offers and update job running times."""
        for match in self.current_matched_offers:
            self.make_match_decision(match)
        self.update_job_running_times()
        self.current_matched_offers.clear()
