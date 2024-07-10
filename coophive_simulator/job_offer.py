from coophive_simulator.data_attribute import DataAttribute
from coophive_simulator.job_offer_attributes_dict import job_offer_attributes


class JobOffer(DataAttribute):
    def __init__(self):
        super().__init__()
        self.data_attributes = job_offer_attributes
