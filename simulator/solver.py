from service_provider import ServiceProvider
from job_offer import JobOffer
from resource_offer import ResourceOffer
from deal import Deal


class Solver(ServiceProvider):
    def __init__(self, address: str, url: str):
        super().__init__(address, url)
        self.machine_keys = ['CPU', 'RAM']
        self.deal_events = []

    def match_job_offer(self, job_offer: JobOffer):
        # only look for exact matches for now
        job_offer_id = job_offer.get_id()
        job_offer_data = job_offer.get_job_offer_data()
        # job_offer_data_items = job_offer_data.items()
        current_resource_offers = self.local_information.get_resource_offers()
        for resource_offer_id, resource_offer in current_resource_offers.items():
            resource_offer_data = resource_offer.get_resource_offer_data()
            # resource_offer_data_items = resource_offer_data.items()
            is_match = True
            for machine_key in self.machine_keys:
                # if resource_offer_data_items[machine_key] != job_offer_data_items[machine_key]:
                if resource_offer_data[machine_key] != job_offer_data[machine_key]:
                    is_match = False

            if is_match:
                return job_offer_id, resource_offer_id

        return False

    def create_deal(self, job_offer: JobOffer, resource_offer: ResourceOffer) -> Deal:
        # deal in stage 1 solver is exact match
        deal = Deal()
        job_offer_data = job_offer.get_job_offer_data()
        resource_offer_data = resource_offer.get_resource_offer_data()
        deal.add_data("resource_provider_address", resource_offer_data['owner'])
        deal.add_data("job_creator_address", job_offer_data['owner'])
        deal.add_data("resource_offer", resource_offer.get_id())
        deal.add_data("job_offer", job_offer.get_id())

        return deal

    def get_deal_events(self):
        return self.deal_events

    def emit_deal_event(self, deal: Deal):
        self.deal_events.append(deal)

    def add_deal_to_smart_contract(self, deal: Deal):
        pass
