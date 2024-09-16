"""Define the Deal class which extends DataAttribute."""

from coophive.data_attribute import DataAttribute

deal_attributes = {
    "seller_provider_address",
    "buyer_address",
    "resource_offer",
    "job_offer",
    "price_per_instruction",
    "expected_number_of_instructions",
    "expected_benefit_to_buyer",
    "buyer_deposit",
    "timeout",
    "timeout_deposit",
    "cheating_collateral_multiplier",
    "benefit_to_buyer",
    "verification_method",
    "mediators",
}


class Deal(DataAttribute):
    """Represents a deal object that inherits from DataAttribute."""

    def __init__(self):
        """Initializes a Deal object."""
        super().__init__()
        self.data_attributes = deal_attributes

    def get_data(self):
        """Get data from attributes."""
        data = {}
        for attribute in self.data_attributes:
            data[attribute] = getattr(self, attribute, None)
        return data

    def set_attributes(self, attributes):
        """Set attributes."""
        for key, value in attributes.items():
            if hasattr(self, key) or key in self.data_attributes:
                setattr(self, key, value)
