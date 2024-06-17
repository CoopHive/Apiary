from data_attribute import DataAttribute
from resource_offer_attributes_dict import resource_offer_attributes


class ResourceOffer(DataAttribute):
    def __init__(self):
        super().__init__()
        self.data_attributes = resource_offer_attributes
        self.data_attributes['T_accept'] = self.calculate_T_accept()
        self.data_attributes['T_reject'] = self.calculate_T_reject()
    
    def calculate_T_accept(self):
        # Placeholder logic for T_accept
        # TODO: Implement logic for calculating T_accept
        return self.data_attributes.get('price_per_instruction', 0) * self.data_attributes.get('expected_number_of_instructions', 0) * 1.05
    
    def calculate_T_reject(self):
        # Placeholder logic for T_reject
        # TODO: Implement logic for calculating T_reject
        return self.data_attributes.get('price_per_instruction', 0) * self.data_attributes.get('expected_number_of_instructions', 0) * 0.95
