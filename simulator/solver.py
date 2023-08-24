from service_provider import ServiceProvider
from job_offer import JobOffer
from resource_offer import ResourceOffer
from deal import Deal
from match import Match
from event import Event


class Solver(ServiceProvider):
    def __init__(self, public_key: str, url: str):
        super().__init__(public_key)
        self.url = url
        self.machine_keys = ['CPU', 'RAM']

    def solve(self):
        for job_offer_id, job_offer in self.get_local_information().get_job_offers().items():
            resulting_resource_offer = self.match_job_offer(job_offer)
            if resulting_resource_offer is not None:
                match = self.create_match(job_offer, resulting_resource_offer)
                match.set_id()
                match_event = Event(name='match', data=match)
                self.emit_event(match_event)

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

    def create_match(self, job_offer: JobOffer, resource_offer: ResourceOffer) -> Match:
        # deal in stage 1 solver is exact match
        match = Match()
        job_offer_data = job_offer.get_data()
        resource_offer_data = resource_offer.get_data()
        match.add_data("resource_provider_address", resource_offer_data['owner'])
        match.add_data("client_address", job_offer_data['owner'])
        match.add_data("resource_offer", resource_offer.get_id())
        match.add_data("job_offer", job_offer.get_id())

        return match

    def get_url(self):
        return self.url

    def add_deal_to_smart_contract(self, deal: Deal):
        pass
