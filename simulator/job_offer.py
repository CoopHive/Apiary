from data_attribute import DataAttribute
from job_offer_attributes_dict import job_offer_attributes


class JobOffer(DataAttribute):
    def __init__(self):
        super().__init__()
        self.data_attributes = job_offer_attributes
