from service_provider import ServiceProvider
from job_offer import JobOffer
from resource_offer import ResourceOffer
from deal import Deal
from match import Match
from event import Event
from smart_contract import SmartContract


class Solver(ServiceProvider):
    def __init__(self, public_key: str, url: str):
        super().__init__(public_key)
        self.url = url
        self.machine_keys = ['CPU', 'RAM']
        self.smart_contract = None
        self.deals_made_in_current_step = []

    def connect_to_smart_contract(self, smart_contract: SmartContract):
        self.smart_contract = smart_contract
        smart_contract.subscribe_event(self.handle_smart_contract_event)

    def handle_smart_contract_event(self, event):
        print(f"I, the Solver have smart contract event {event.get_name(), event.get_data().get_id()}")
        # if deal, remove resource and job offers from list
        if event.get_name() == 'deal':
            deal = event.get_data()
            self.deals_made_in_current_step.append(deal)

    def remove_outdated_offers(self):
        for deal in self.deals_made_in_current_step:
            deal_data = deal.get_data()
            # delete resource offer
            resource_offer = deal_data['resource_offer']
            del self.get_local_information().get_resource_offers()[resource_offer]
            # delete job offer
            job_offer = deal_data['job_offer']
            del self.get_local_information().get_job_offers()[job_offer]
        # clear list of deals made in current step
        self.deals_made_in_current_step.clear()

    def solve(self):
        for job_offer_id, job_offer in self.get_local_information().get_job_offers().items():
            resulting_resource_offer = self.match_job_offer(job_offer)
            if resulting_resource_offer is not None:
                match = self.create_match(job_offer, resulting_resource_offer)
                match.set_id()
                match_event = Event(name='match', data=match)
                self.emit_event(match_event)
        # remove outdated job and resource offers
        self.remove_outdated_offers()

    def match_job_offer(self, job_offer: JobOffer):
        # only look for exact matches for now
        job_offer_data = job_offer.get_data()
        current_resource_offers = self.local_information.get_resource_offers()
        for resource_offer_id, resource_offer in current_resource_offers.items():
            resource_offer_data = resource_offer.get_data()
            is_match = True
            for machine_key in self.machine_keys:
                if resource_offer_data[machine_key] != job_offer_data[machine_key]:
                    is_match = False

            if is_match:
                return resource_offer

        return None

    def add_random_match_data(self, match):
        match.add_data("client_deposit", 5)
        match.add_data("timeout", 10)
        match.add_data("timeout_deposit", 3)
        match.add_data("cheating_collateral_multiplier", 50)

    def create_match(self, job_offer: JobOffer, resource_offer: ResourceOffer) -> Match:
        # deal in stage 1 solver is exact match
        match = Match()
        job_offer_data = job_offer.get_data()
        resource_offer_data = resource_offer.get_data()
        match.add_data("resource_provider_address", resource_offer_data['owner'])
        match.add_data("client_address", job_offer_data['owner'])
        match.add_data("resource_offer", resource_offer.get_id())
        match.add_data("job_offer", job_offer.get_id())

        self.add_random_match_data(match)

        return match

    def get_url(self):
        return self.url

    def add_deal_to_smart_contract(self, deal: Deal):
        pass
