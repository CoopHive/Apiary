import logging
import os

from coophive_simulator.deal import Deal
from coophive_simulator.event import Event
from coophive_simulator.job_offer import JobOffer

# JSON logging helper function
from coophive_simulator.log_json import log_json
from coophive_simulator.match import Match
from coophive_simulator.resource_offer import ResourceOffer
from coophive_simulator.service_provider import ServiceProvider
from coophive_simulator.smart_contract import SmartContract
from coophive_simulator.utils import *


class Solver(ServiceProvider):
    def __init__(self, public_key: str, url: str):
        super().__init__(public_key)
        self.logger = logging.getLogger(f"Solver {self.public_key}")
        logging.basicConfig(
            filename=f"{os.getcwd()}/local_logs", filemode="w", level=logging.DEBUG
        )
        self.url = url
        self.machine_keys = ["CPU", "RAM"]
        self.smart_contract = None
        self.deals_made_in_current_step = []
        self.currently_matched_job_offers = set()
        self.current_matched_resource_offers = set()

    def connect_to_smart_contract(self, smart_contract: SmartContract):
        self.smart_contract = smart_contract
        smart_contract.subscribe_event(self.handle_smart_contract_event)

    def handle_smart_contract_event(self, event):
        if event.get_name() == "mediation_random":
            event_name = event.get_name()
            event_data_id = event.get_data().get_id() if event.get_data() else None
            log_json(
                self.logger,
                "Smart contract event",
                {"event_name": event_name, "event_data_id": event_data_id},
            )
            # self.logger.info(f"have smart contract event {event.get_name()}")
            job_offer_cid = event.get_data()
            if job_offer_cid not in self.get_local_information().get_job_offers():
                # solver doesn't have the job offer locally, must retrieve from IPFS
                job_offer = self.get_local_information().ipfs.get(job_offer_cid)
            else:
                job_offer = self.get_local_information().get_job_offers()[job_offer_cid]

            event = (
                job_offer  # self.get_local_information().get_job_offers()[job_offer]
            )

        # if deal, remove resource and job offers from list
        elif event.get_name() == "deal":
            self.logger.info(
                f"have smart contract event {event.get_name(), event.get_data().get_id()}"
            )
            deal = event.get_data()
            self.deals_made_in_current_step.append(deal)

    def _remove_offer(self, offers_dict, offer_id):
        """Helper function to remove an offer by ID."""
        if offer_id in offers_dict:
            del offers_dict[offer_id]

    def remove_outdated_offers(self):
        # print([deal.get_id() for deal in self.deals_made_in_current_step])
        for deal in self.deals_made_in_current_step:
            deal_data = deal.get_data()
            # delete resource offer
            resource_offer = deal_data["resource_offer"]
            # print(deal.get_id())
            # print(f"resource_offer {resource_offer}")
            # print(self.get_local_information().get_resource_offers())
            # del self.get_local_information().get_resource_offers()[resource_offer]
            # delete job offer
            job_offer = deal_data["job_offer"]
            self._remove_offer(
                self.get_local_information().get_resource_offers(), resource_offer
            )
            self._remove_offer(self.get_local_information().get_job_offers(), job_offer)
            # del self.get_local_information().get_job_offers()[job_offer]
        # clear list of deals made in current step
        self.deals_made_in_current_step.clear()

    def solver_cleanup(self):
        self.currently_matched_job_offers.clear()
        self.current_matched_resource_offers.clear()
        # remove outdated job and resource offers
        self.remove_outdated_offers()

    def solve(self):
        # print()
        # print(self.get_local_information().get_job_offers().items())
        for job_offer_id, job_offer in (
            self.get_local_information().get_job_offers().items()
        ):
            resulting_resource_offer = self.match_job_offer(job_offer)
            if resulting_resource_offer is not None:
                # add job and resource offers to sets of currently matched offers
                resulting_resource_offer_id = resulting_resource_offer.get_id()
                self.current_matched_resource_offers.add(resulting_resource_offer_id)
                self.currently_matched_job_offers.add(job_offer_id)
                # create match
                match = self.create_match(job_offer, resulting_resource_offer)
                match.set_id()
                # create match event
                match_event = Event(name="match", data=match)
                # emit match event
                self.emit_event(match_event)
                # go on to the next job offer
                continue

    def match_job_offer(self, job_offer: JobOffer):
        # only look for exact matches for now
        job_offer_data = job_offer.get_data()
        job_offer_id = job_offer.get_id()
        current_resource_offers = self.local_information.get_resource_offers()
        for resource_offer_id, resource_offer in current_resource_offers.items():
            # do not consider offers that have already been matched
            if (job_offer_id in self.currently_matched_job_offers) or (
                resource_offer_id in self.current_matched_resource_offers
            ):
                continue
            resource_offer_data = resource_offer.get_data()
            is_match = True
            for machine_key in self.machine_keys:
                if resource_offer_data[machine_key] != job_offer_data[machine_key]:
                    is_match = False

            if is_match:
                return resource_offer

        return None

    def add_necessary_match_data(self, match):
        for data_field, data_value in extra_necessary_match_data.items():
            match.add_data(data_field, data_value)

    def create_match(self, job_offer: JobOffer, resource_offer: ResourceOffer) -> Match:
        # deal in stage 1 solver is exact match
        match = Match()
        job_offer_data = job_offer.get_data()
        resource_offer_data = resource_offer.get_data()
        match.add_data("resource_provider_address", resource_offer_data["owner"])
        match.add_data("client_address", job_offer_data["owner"])
        match.add_data("resource_offer", resource_offer.get_id())
        match.add_data("job_offer", job_offer.get_id())

        self.add_necessary_match_data(match)

        return match

    def get_url(self):
        return self.url

    def add_deal_to_smart_contract(self, deal: Deal):
        pass
