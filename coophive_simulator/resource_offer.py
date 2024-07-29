"""Define the ResourceOffer class which extends DataAttribute."""

from coophive_simulator.data_attribute import DataAttribute

resource_offer_attributes = {
    "owner",
    "machine_id",
    "target_client",
    "created_at",
    "timeout",
    "CPU",
    "GPU",
    "RAM",
    "prices",
    "verification_method",
    "mediators",
    # "price_per_instruction", # value in dollars (TODO: Should this be in the resource_offer?)
    # "expected_number_of_instructions" #(TODO: Should this be in the resource_offer?)
}


class ResourceOffer(DataAttribute):
    """Represents a resource-offer object that inherits from DataAttribute."""

    def __init__(self):
        """Initializes a ResourceOffer object."""
        super().__init__()
        self.data_attributes = resource_offer_attributes
        self.data_attributes["T_accept"] = self.calculate_T_accept()
        self.data_attributes["T_reject"] = self.calculate_T_reject()

    def calculate_T_accept(self):
        """Placeholder logic for T_accept."""
        # TODO: Implement logic for calculating T_accept
        return (
            self.data_attributes.get("price_per_instruction", 0)
            * self.data_attributes.get("expected_number_of_instructions", 0)
            * 1.05
        )

    def calculate_T_reject(self):
        """Placeholder logic for T_reject."""
        # TODO: Implement logic for calculating T_reject
        return (
            self.data_attributes.get("price_per_instruction", 0)
            * self.data_attributes.get("expected_number_of_instructions", 0)
            * 0.95
        )

    def set_attributes(self, attributes):
        """Set attributes."""
        for key, value in attributes.items():
            setattr(self, key, value)

    def get_data(self):
        """Get data from attributes."""
        data = {}
        for attribute in self.data_attributes:
            data[attribute] = getattr(self, attribute, None)
        return data
