from coophive_simulator.data_attribute import DataAttribute
from coophive_simulator.resource_offer_attributes_dict import resource_offer_attributes


class ResourceOffer(DataAttribute):
    def __init__(self):
        super().__init__()
        self.data_attributes = resource_offer_attributes
