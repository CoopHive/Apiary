"""Define the Match class which extends DataAttribute and provides functionality related to matching attributes and signing."""

from coophive.data_attribute import DataAttribute

match_attributes = {
    "seller_address",
    "buyer_address",
    "resource_offer",
    "job_offer",
    "price_per_instruction",  # [USD]
    "expected_number_of_instructions",
    "expected_benefit_to_buyer",  # [USD]
    "buyer_deposit",
    "timeout",  # [s]
    "timeout_deposit",
    "cheating_collateral_multiplier",
    "verification_method",
    "mediators",
    "rounds_completed",
}


class Match(DataAttribute):
    """Represents a match object that inherits from DataAttribute."""

    def __init__(self, data=None):
        """Initializes a Match object."""
        super().__init__()
        self.data_attributes = match_attributes
        self.buyer_signed = False
        self.seller_signed = False
        if data:
            for key, value in data.items():
                self.add_data(key, value)

    def get_seller_signed(self):
        """Get the status of seller signed flag."""
        return self.seller_signed

    def get_buyer_signed(self):
        """Get the status of buyer signed flag."""
        return self.buyer_signed

    def sign_seller(self):
        """Set the seller signed flag to True."""
        self.seller_signed = True

    def sign_buyer(self):
        """Set the buyer signed flag to True."""
        self.buyer_signed = True

    def get_data(self):
        """Get data from attributes."""
        data = {}
        for attribute in self.data_attributes:
            data[attribute] = getattr(self, attribute, None)
        return data

    def set_attributes(self, attributes):
        """Set attributes."""
        for key, value in attributes.items():
            setattr(self, key, value)

    def add_data(self, data_field, data_value):
        """Different API to set attributes."""
        setattr(self, data_field, data_value)
