"""Define the JobOffer class which extends DataAttribute."""

from coophive_simulator.data_attribute import DataAttribute

job_offer_attributes = {
    "owner",
    "target_client",
    "created_at",
    "timeout",
    "CPU",
    "GPU",
    "RAM",
    "module",
    "prices",
    # TODO: add instruction count
    "verification_method",
    "mediators",
}


class JobOffer(DataAttribute):
    """Represents a job-offer object that inherits from DataAttribute."""

    def __init__(self):
        """Initializes a JobOffer object."""
        super().__init__()
        self.data_attributes = job_offer_attributes

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
