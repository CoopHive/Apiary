"""This module defines the SmartContract class.

It handles the operations and logic associated with smart contracts, including transactions, deals, matches, and results.
"""

import logging
import os

from coophive_simulator.deal import Deal
from coophive_simulator.event import Event
from coophive_simulator.log_json import log_json
from coophive_simulator.match import Match
from coophive_simulator.result import Result
from coophive_simulator.service_provider import ServiceProvider
from coophive_simulator.utils import Tx


class SmartContract(ServiceProvider):
    """A class to represent a smart contract.

    This class extends the ServiceProvider class and provides methods to handle
    the lifecycle of a smart contract including creating deals, handling matches,
    posting results, and managing balances.
    """

    def __init__(self, public_key: str):
        """Initialize the SmartContract with a public key.

        Args:
            public_key (str): The public key for the smart contract.
        """
        super().__init__(public_key)
        self.logger = logging.getLogger(f"Smart Contract {self.public_key}")
        logging.basicConfig(
            filename=f"{os.getcwd()}/local_logs", filemode="w", level=logging.DEBUG
        )
        self.transactions = []
        self.deals: dict[str, Deal] = {} # type: ignore # mapping from deal id to deal
        self.balances = {}  # mapping from public key to balance
        self.balance = 0  # total balance in the contract
        self.matches_made_in_current_step: list[Match] = []
        self.results_posted_in_current_step = []

    def _agree_to_match_resource_provider(self, match: Match, tx: Tx):
        """Handle the resource provider's agreement to a match."""
        match_data = match.get_data()
        timeout_deposit = match_data["timeout_deposit"]
        if tx.value != timeout_deposit:
            logging.info(
                f'transaction value of {tx.value} does not match timeout deposit {match_data["timeout_deposit"]}'
            )
            raise Exception("transaction value does not match timeout deposit")
        resource_provider_address = match_data["resource_provider_address"]
        self.balances[resource_provider_address] -= timeout_deposit
        self.balance += timeout_deposit
        match.sign_resource_provider()
        # self.logger.info(f"resource provider {match.get_data()['resource_provider_address']} has signed match {match.get_id()}")

        log_data = {
            "resource_provider_address": resource_provider_address,
            "match_id": match.get_id(),
        }
        log_json(self.logger, "Resource provider signed match", log_data)

    def _agree_to_match_client(self, match: Match, tx: Tx):
        """Handle the client's agreement to a match."""
        match_data = match.get_data()
        client_deposit = match_data["client_deposit"]
        if tx.value != client_deposit:
            logging.info(
                f'transaction value of {tx.value} does not match client deposit {match_data["client_deposit"]}'
            )
            raise Exception("transaction value does not match timeout deposit")
        client_address = match_data["client_address"]
        if client_deposit > self.balances[client_address]:
            logging.info(
                f"transaction value of {tx.value} exceeds client balance of {self.balances[client_address]}"
            )
            raise Exception("transaction value exceeds balance")
        self.balances[client_address] -= tx.value
        self.balance += tx.value
        match.sign_client()
        # self.logger.info(f"client {match.get_data()['client_address']} has signed match {match.get_id()}")

        log_data = {"client_address": client_address, "match_id": match.get_id()}
        log_json(self.logger, "Client signed match", log_data)

    def agree_to_match(self, match: Match, tx: Tx):
        """Handle agreement to a match by either the resource provider or client.

        Args:
            match (Match): The match object.
            tx (Tx): The transaction object.
        """
        if match.get_data().get('resource_provider_address') == tx.sender:
            self._agree_to_match_resource_provider(match, tx)
        elif match.get_data().get('client_address') == tx.sender:
            self._agree_to_match_client(match, tx)
        if match.get_resource_provider_signed() and match.get_client_signed():
            self.matches_made_in_current_step.append(match)

    def _create_deal(self, match: Match):
        deal = Deal()
        for data_field, data_value in match.get_data().items():
            deal.add_data(data_field, data_value)
        # TODO: this is for testing purposes, should not be added here manually
        deal.add_data("actual_honest_time_to_completion", 1)
        deal.set_id()
        self.deals[deal.get_id()] = deal
        deal_event = Event(name="deal", data=deal)
        self.emit_event(deal_event)

        log_json(
            self.logger,
            "Deal created",
            {"deal_id": deal.get_id(), "deal_attributes": deal.get_data()},
        )
        # append to transactions
        self.transactions.append(deal_event)

    def _refund_timeout_deposit(self, result: Result):
        deal_id = result.get_data()["deal_id"]
        deal_data = self.deals[deal_id].get_data()
        timeout_deposit = deal_data["timeout_deposit"]
        resource_provider_address = deal_data["resource_provider_address"]
        self.balances[resource_provider_address] += timeout_deposit
        self.balance -= timeout_deposit
        log_json(
            self.logger,
            "Timeout deposit refunded",
            {
                "timeout_deposit": timeout_deposit,
                "resource_provider_address": resource_provider_address,
            },
        )

    def _post_cheating_collateral(self, result: Result, tx: Tx):
        deal_id = result.get_data()["deal_id"]
        deal_data = self.deals[deal_id].get_data()
        cheating_collateral_multiplier = deal_data["cheating_collateral_multiplier"]
        instruction_count = result.get_data()["instruction_count"]
        intended_cheating_collateral = (
            cheating_collateral_multiplier * instruction_count
        )
        if intended_cheating_collateral != tx.value:
            log_json(
                self.logger,
                "Cheating collateral deposit does not match needed",
                {
                    "transaction_value": tx.value,
                    "needed_cheating_collateral": intended_cheating_collateral,
                },
            )
            raise Exception(
                "transaction value does not match needed cheating collateral"
            )
        resource_provider_address = deal_data["resource_provider_address"]
        if intended_cheating_collateral > self.balances[resource_provider_address]:
            log_json(
                self.logger,
                "Transaction value exceeds resource provider balance",
                {
                    "transaction_value": tx.value,
                    "resource_provider_balance": self.balances[
                        resource_provider_address
                    ],
                    "resource_provider_address": resource_provider_address,
                },
            )
            raise Exception("transaction value exceeds balance")
        self.balances[resource_provider_address] -= tx.value
        self.balance += tx.value

    # TODO: add returning of cheating collateral
    def refund_cheating_collateral(self, result: Result):
        """Refund the cheating collateral based on the result.

        Args:
            result (Result): The result object.
        """
        deal_id = result.get_data()["deal_id"]
        deal_data = self.deals[deal_id].get_data()
        cheating_collateral_multiplier = deal_data["cheating_collateral_multiplier"]
        instruction_count = result.get_data()["instruction_count"]
        intended_cheating_collateral = (
            cheating_collateral_multiplier * instruction_count
        )
        resource_provider_address = deal_data["resource_provider_address"]
        self.balances[resource_provider_address] += intended_cheating_collateral
        self.balance -= intended_cheating_collateral

    def _create_and_emit_result_events(self):
        for result, tx in self.results_posted_in_current_step:
            if not isinstance(result, Result):
                raise TypeError("result must be an instance of Result")
            else: 
                deal_id = result.get_data().get('deal_id')
                if self.deals[deal_id].get_data()['resource_provider_address'] == tx.sender:
                    result_event = Event(name='result', data=result)
                    self.emit_event(result_event)
                    self._refund_timeout_deposit(result)
                    # append to transactions
                    self.transactions.append(result_event)

    def _account_for_cheating_collateral_payments(self):
        for result, tx in self.results_posted_in_current_step:
            self._post_cheating_collateral(result, tx)

    def post_result(self, result: Result, tx: Tx):
        """Post a result and add it to the results posted in the current step."""
        self.results_posted_in_current_step.append([result, tx])

    def _refund_client_deposit(self, deal: Deal):
        """Refund the client's deposit based on the deal."""
        client_address = deal.get_data()["client_address"]
        client_deposit = deal.get_data().get('client_deposit')
        self.balance -= client_deposit
        self.balances[client_address] += client_deposit

    def post_client_payment(self, result: Result, tx: Tx):
        """Post a payment from the client based on the result."""
        result_data = result.get_data()
        result_instruction_count = result_data["instruction_count"]
        result_instruction_count = float(result_instruction_count)
        deal_id = result_data["deal_id"]
        deal_data = self.deals.get(deal_id).get_data()
        price_per_instruction = deal_data["price_per_instruction"]
        expected_payment_value = result_instruction_count * price_per_instruction
        if tx.value != expected_payment_value:
            logging.info(
                f"transaction value of {tx.value} does not match expected payment value {expected_payment_value}"
            )
            raise Exception("transaction value does not match expected payment value")
        client_address = deal_data["client_address"]
        if expected_payment_value > self.balances[client_address]:
            logging.info(
                f"transaction value of {tx.value} exceeds client balance of {self.balances[client_address]}"
            )
            raise Exception("transaction value exceeds balance")
        # subtract from client's deposit
        self.balances[client_address] -= tx.value
        # add transaction value to smart contract balance
        self.balance += tx.value
        deal = self.deals[deal_id]
        resource_provider_address = deal.get_data()["resource_provider_address"]
        # pay resource provider
        self.balances[resource_provider_address] += tx.value
        # subtract from smart contract balance
        self.balance -= tx.value
        # refund client deposit
        self._refund_client_deposit(deal)

    def fund(self, tx: Tx):
        """Fund the smart contract with a transaction."""
        self.balances[tx.sender] = self.balances.get(tx.sender, 0) + tx.value

    def slash_cheating_collateral(self, event: Event, result: Result):
        """Slash the cheating collateral based on an event."""
        deal_id = event.get_data()["deal_id"]
        deal_data = self.deals[deal_id].get_data()
        cheating_collateral_multiplier = deal_data["cheating_collateral_multiplier"]
        instruction_count = event.get_data()["instruction_count"]
        intended_cheating_collateral = (
            cheating_collateral_multiplier * instruction_count
        )
        resource_provider_address = deal_data["resource_provider_address"]
        self.balances[resource_provider_address] -= intended_cheating_collateral
        self.balance += intended_cheating_collateral

    def ask_consortium_of_mediators(self, event: Event):
        """Ask a consortium of mediators to check the result.

        Args:
            event (Event): The event object.

        Returns:
            bool: True if the result was correct, False otherwise.
        """
        return True  # TODO: remove default boolean.

    def ask_random_mediator(self, event: Event):
        """Ask a random mediator to check the result.

        In order to check result, some entity needs to submit the job offer
        this can be any of the client, the compute node, the solver, or the smart contract
        doesn't make sense for it to be the solver
        if the smart contract does it, then it needs to know the method of verification beforehand,
        meaning that the verification method needs to be described in the deal
        the alternative is that either the client or compute node call the verification, but in that case,
        they need to agree anyway, and it makes sense for the smart contract to be doing the call.

        In order to create a job, the smart contract must extract the job spec from the deal data,
        and emit an event indicating that the solver should find compute nodes that can run the job,
        and then choose one randomly
        """
        result = event.get_data()
        deal_id = result.get_data()["deal_id"]
        deal_data = self.deals[deal_id].get_data()
        job_offer = deal_data["job_offer"]
        logging.info(job_offer)

        # TODO: job offer is just a string, need to get the actual job offer object
        # otherwise event.get_data().get_id() in e.g. line 30 of solver.py will throw an error
        mediation_request_event = Event(name="mediation_random", data=job_offer)
        self.emit_event(mediation_request_event)

        """
        this is all wrong
        the potential mediators need to be agreed upon beforehand
        but how do we know that they have the correct resources, or that they're even available?
        maybe intersection of the set of potential mediators and set of nodes that have the resources?
        
        alternatively, keep trying random mediators until one is available
        """

        # how to determine the random mediator from the available ones?
        # 1) smart contract emits mediation request event
        # 2) solver receives mediation request event, sorts the mediators by their ids,
        #    and puts the list into an IPFS CID
        # 3) solver submits the CID to the smart contract
        # 4) smart contract picks a random number (e.g. from drand),
        #    and then picks the index of the mediator to be the number of potential mediators % random number
        # 5) smart contract emits mediation request event
        # 6) solver handles mediation request event, and matches the job offer with the selected mediator
        # 7) if any of these steps fail, start over

        # if result was correct, return True
        return True
        # if result was incorrect, return False
        # return False

    def mediate_result(self, event: Event, result: Result, tx: Tx = None):
        """Mediate the result based on the specified verification method.

        Args:
            event (Event): The event object.
            tx (Tx, optional): The transaction object. Defaults to None.
        """
        result = event.get_data()
        deal_id = result.get_data()["deal_id"]
        deal_data = self.deals[deal_id].get_data()
        verification_method = deal_data["verification_method"]

        if verification_method is None:
            # if there is no verification method specified, assume that the result is correct
            mediation_flag = True
        elif verification_method == "random":
            mediation_flag = self.ask_random_mediator(event)
        elif verification_method == "consortium":
            mediation_flag = self.ask_consortium_of_mediators(event)

        if mediation_flag == True:
            # if result was correct, then compute node gets paid and returned its collateral,
            # client gets paid back its deposit, but pays for the mediation
            pass
        elif mediation_flag == False:
            # if result was incorrect, then client gets returned its collateral, and compute node gets slashed
            self.slash_cheating_collateral(event)

    def _log_balances(self):
        # self.logger.info(f"Smart Contract balance: {self.balance}")
        # self.logger.info(f"Smart Contract balances: {self.balances}")

        log_json(self.logger, "Smart Contract balance", {"balance": self.balance})
        log_json(self.logger, "Smart Contract balances", {"balances": self.balances})

    def _get_balances(self):
        return self.balances

    def _get_balance(self):
        return self.balance

    def _smart_contract_loop(self):
        for match in self.matches_made_in_current_step:
            resource_provider_address = match.get_data()["resource_provider_address"]
            client_address = match.get_data()["client_address"]
            match_id = match.get_id()
            match_data = match.get_data()
            self.logger.info(
                f"Both resource provider {resource_provider_address} and client {client_address} have signed match {match_id}"
            )

            log_json(
                self.logger,
                "Match attributes",
                {"match_id": match_id, "match_attributes": match_data},
            )
            self._create_deal(match)
            # self.logger.info(f"both resource provider {match.get_data()['resource_provider_address']} and client {match.get_data()['client_address']} have signed match {match.get_id()}")
            # self.logger.info(f"match attributes of match {match.get_id()}: {match.get_data()}")
            # self._create_deal(match)
        self._create_and_emit_result_events()
        self._account_for_cheating_collateral_payments()
        self.matches_made_in_current_step.clear()
        self.results_posted_in_current_step.clear()
        self._log_balances()
