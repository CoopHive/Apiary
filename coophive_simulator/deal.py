"""Define the Deal class which extends DataAttribute."""

from coophive_simulator.data_attribute import DataAttribute

# TODO: add "job" to deal attributes
deal_attributes = {
    "resource_provider_address",
    "client_address",
    "resource_offer",
    "job_offer",
    "price_per_instruction",
    "expected_number_of_instructions",
    "expected_benefit_to_client",
    "client_deposit",
    "timeout",
    "timeout_deposit",
    "cheating_collateral_multiplier",
    "actual_honest_time_to_completion",
    "actual_cost_to_resource_provider",
    "actual_benefit_to_client",
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
