"""Define the Match class which extends DataAttribute and provides functionality related to matching attributes and signing."""

from coophive.data_attribute import DataAttribute

match_attributes = {
    "resource_provider_address",
    "client_address",
    "resource_offer",
    "job_offer",
    "price_per_instruction",  # [USD]
    "expected_number_of_instructions",
    "expected_benefit_to_client",  # [USD]
    "client_deposit",
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
        self.client_signed = False
        self.resource_provider_signed = False
        if data:
            for key, value in data.items():
                self.add_data(key, value)

    def get_resource_provider_signed(self):
        """Get the status of resource provider signed flag."""
        return self.resource_provider_signed

    def get_client_signed(self):
        """Get the status of client signed flag."""
        return self.client_signed

    def sign_resource_provider(self):
        """Set the resource provider signed flag to True."""
        self.resource_provider_signed = True

    def sign_client(self):
        """Set the client signed flag to True."""
        self.client_signed = True

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
