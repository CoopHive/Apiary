from data_attribute import DataAttribute
from job_offer_attributes_dict import job_offer_attributes


class JobOffer(DataAttribute):
    def __init__(self):
        super().__init__()
        self.data_attributes = job_offer_attributes
        
    def set_attributes(self, attributes):
        for key, value in attributes.items():
            setattr(self, key, value)
            
    def get_data(self):
        data = {}
        for attribute in self.data_attributes:
            data[attribute] = getattr(self, attribute, None)
        return data
