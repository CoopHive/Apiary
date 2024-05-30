from data_attribute import DataAttribute
from resource_offer_attributes_dict import resource_offer_attributes


class ResourceOffer(DataAttribute):
    def __init__(self):
        super().__init__()
        self.data_attributes = resource_offer_attributes
        
    def set_attributes(self, attributes):
        
        for key, value in attributes.items():
            setattr(self, key, value)
            
    def get_data(self):
        data = {}
        for attribute in self.data_attributes:
            data[attribute] = getattr(self, attribute, None)
        return data