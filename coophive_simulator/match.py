from coophive_simulator.data_attribute import DataAttribute
from coophive_simulator.match_attributes_dict import match_attributes


class Match(DataAttribute):
    def __init__(self):
        super().__init__()
        self.data_attributes = match_attributes
        self.client_signed = False
        self.resource_provider_signed = False

    def get_resource_provider_signed(self):
        return self.resource_provider_signed

    def get_client_signed(self):
        return self.client_signed

    def sign_resource_provider(self):
        self.resource_provider_signed = True

    def sign_client(self):
        self.client_signed = True
