"""This module defines the SmartContract class.

It handles the operations and logic associated with smart contracts, including transactions, deals, matches, and results.
"""

import logging

from coophive.deal import Deal
from coophive.event import Event
from coophive.match import Match
from coophive.result import Result
from coophive.utils import Tx, log_json


class SmartContract:
    """A class to represent a smart contract.

    This class provides methods to handle the lifecycle of a smart contract
    including creating deals, handling matches, posting results, and managing balances.
    """

    def __init__(self, public_key: str):
        """Initialize the SmartContract with a public key.

        Args:
            public_key (str): The public key for the smart contract.
        """
        self.public_key = public_key
        self.events = []
        self.event_handlers = []
        self.transactions = []
        self.deals: dict[str, Deal] = {}  # type: ignore # mapping from deal id to deal
        self.balances = {}  # mapping from public key to balance
        self.balance = 0  # total balance in the contract
        self.matches_made_in_current_step: list[Match] = []
        self.results_posted_in_current_step = []

    def _agree_to_match_seller(self, match: Match, tx: Tx):
        """Handle the seller's agreement to a match."""
        match_data = match.get_data()
        timeout_deposit = match_data["timeout_deposit"]
        if tx.value != timeout_deposit:
            logging.info(
                f'transaction value of {tx.value} does not match timeout deposit {match_data["timeout_deposit"]}'
            )
            raise Exception("transaction value does not match timeout deposit")
        seller_address = match_data["seller_address"]
        self.balances[seller_address] -= timeout_deposit
        self.balance += timeout_deposit
        match.sign_seller()

        log_data = {
            "seller_address": seller_address,
            "match_id": match.get_id(),
        }
        log_json("Resource provider signed match", log_data)

    def _agree_to_match_buyer(self, match: Match, tx: Tx):
        """Handle the buyer's agreement to a match."""
        match_data = match.get_data()
        buyer_deposit = match_data["buyer_deposit"]
        if tx.value != buyer_deposit:
            logging.info(
                f'transaction value of {tx.value} does not match buyer deposit {match_data["buyer_deposit"]}'
            )
            raise Exception("transaction value does not match timeout deposit")
        buyer_address = match_data["buyer_address"]
        if buyer_deposit > self.balances[buyer_address]:
            logging.info(
                f"transaction value of {tx.value} exceeds buyer balance of {self.balances[buyer_address]}"
            )
            raise Exception("transaction value exceeds balance")
        self.balances[buyer_address] -= tx.value
        self.balance += tx.value
        match.sign_buyer()

        log_data = {"buyer_address": buyer_address, "match_id": match.get_id()}
        log_json("Client signed match", log_data)

    def agree_to_match(self, match: Match, tx: Tx):
        """Handle agreement to a match by either the seller or buyer.

        Args:
            match (Match): The match object.
            tx (Tx): The transaction object.
        """
        if match.get_data().get("seller_address") == tx.sender:
            self._agree_to_match_seller(match, tx)
        elif match.get_data().get("buyer_address") == tx.sender:
            self._agree_to_match_buyer(match, tx)
        if match.seller_signed and match.buyer_signed:
            self.matches_made_in_current_step.append(match)

    def subscribe_event(self, handler):
        """Subscribe an event handler to receive emitted events."""
        self.event_handlers.append(handler)

    def emit_event(self, event: Event):
        """Emit an event and notify all subscribed event handlers."""
        self.events.append(event)
        for event_handler in self.event_handlers:
            event_handler(event)

    def _create_deal(self, match: Match):
        logging.info(f"Match data before setting ID: {match.get_data()}")

        deal = Deal()
        for data_field, data_value in match.get_data().items():
            if data_field in deal.get_data().keys():
                deal.add_data(data_field, data_value)
        deal.set_id()
        self.deals[deal.get_id()] = deal
        deal_event = Event(name="deal", data=deal)
        self.emit_event(deal_event)

        log_data = {"deal_id": deal.get_id(), "deal_attributes": deal.get_data()}
        log_json("Deal created", log_data)
        # append to transactions
        self.transactions.append(deal_event)

    def _refund_timeout_deposit(self, result: Result):
        deal_id = result.get_data()["deal_id"]
        deal_data = self.deals[deal_id].get_data()
        timeout_deposit = deal_data["timeout_deposit"]
        seller_address = deal_data["seller_address"]
        self.balances[seller_address] += timeout_deposit
        self.balance -= timeout_deposit
        log_json(
            "Timeout deposit refunded",
            {
                "timeout_deposit": timeout_deposit,
                "seller_address": seller_address,
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
                "Cheating collateral deposit does not match needed",
                {
                    "transaction_value": tx.value,
                    "needed_cheating_collateral": intended_cheating_collateral,
                },
            )
            raise Exception(
                "transaction value does not match needed cheating collateral"
            )
        seller_address = deal_data["seller_address"]
        if intended_cheating_collateral > self.balances[seller_address]:
            log_json(
                "Transaction value exceeds seller balance",
                {
                    "transaction_value": tx.value,
                    "seller_balance": self.balances[seller_address],
                    "seller_address": seller_address,
                },
            )
            raise Exception("transaction value exceeds balance")
        self.balances[seller_address] -= tx.value
        self.balance += tx.value

    def _create_and_emit_result_events(self):
        for result, tx in self.results_posted_in_current_step:
            if not isinstance(result, Result):
                raise TypeError("result must be an instance of Result")
            else:
                deal_id = result.get_data().get("deal_id")
                if self.deals[deal_id].get_data()["seller_address"] == tx.sender:
                    result_event = Event(name="result", data=result)
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

    def _refund_buyer_deposit(self, deal: Deal):
        """Refund the buyer's deposit based on the deal."""
        buyer_address = deal.get_data()["buyer_address"]
        buyer_deposit = deal.get_data().get("buyer_deposit")
        self.balance -= buyer_deposit
        self.balances[buyer_address] += buyer_deposit

    def post_buyer_payment(self, result: Result, tx: Tx):
        """Post a payment from the buyer based on the result."""
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
        buyer_address = deal_data["buyer_address"]
        if expected_payment_value > self.balances[buyer_address]:
            logging.info(
                f"transaction value of {tx.value} exceeds buyer balance of {self.balances[buyer_address]}"
            )
            raise Exception("transaction value exceeds balance")
        # subtract from buyer's deposit
        self.balances[buyer_address] -= tx.value
        # add transaction value to smart contract balance
        self.balance += tx.value
        deal = self.deals[deal_id]
        seller_address = deal.get_data()["seller_address"]
        # pay seller
        self.balances[seller_address] += tx.value
        # subtract from smart contract balance
        self.balance -= tx.value
        # refund buyer deposit
        self._refund_buyer_deposit(deal)

    def slash_cheating_collateral(self, event: Event, result: Result):
        """Slash the cheating collateral based on an event."""
        deal_id = event.data["deal_id"]
        deal_data = self.deals[deal_id].get_data()
        cheating_collateral_multiplier = deal_data["cheating_collateral_multiplier"]
        instruction_count = event.data["instruction_count"]
        intended_cheating_collateral = (
            cheating_collateral_multiplier * instruction_count
        )
        seller_address = deal_data["seller_address"]
        self.balances[seller_address] -= intended_cheating_collateral
        self.balance += intended_cheating_collateral

    def ask_consortium_of_mediators(self, event: Event):
        """Ask a consortium of mediators to check the result (Placeholder)."""
        return True

    def ask_random_mediator(self, event: Event):
        """Ask a random mediator to check the result.

        In order to check result, some entity needs to submit the job offer
        this can be any of the buyer, the seller, the solver, or the smart contract
        doesn't make sense for it to be the solver
        if the smart contract does it, then it needs to know the method of verification beforehand,
        meaning that the verification method needs to be described in the deal
        the alternative is that either the buyer or compute node call the verification, but in that case,
        they need to agree anyway, and it makes sense for the smart contract to be doing the call.

        In order to create a job, the smart contract must extract the job spec from the deal data,
        and emit an event indicating that the solver should find compute nodes that can run the job,
        and then choose one randomly
        """
        result = event.data
        deal_id = result.get_data()["deal_id"]
        deal_data = self.deals[deal_id].get_data()
        job_offer = deal_data["job_offer"]
        logging.info(job_offer)

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
            result (Result): The result object.
            tx (Tx, optional): The transaction object. Defaults to None.
        """
        result = event.data
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
            # buyer gets paid back its deposit, but pays for the mediation
            pass
        elif mediation_flag == False:
            # if result was incorrect, then buyer gets returned its collateral, and compute node gets slashed
            self.slash_cheating_collateral(event)
