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
}


class ResourceOffer(DataAttribute):
    """Represents a resource-offer object that inherits from DataAttribute."""

    def __init__(self):
        """Initializes a ResourceOffer object."""
        super().__init__()
        self.data_attributes = resource_offer_attributes

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
