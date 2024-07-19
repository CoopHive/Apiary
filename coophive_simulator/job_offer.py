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
    "verification_method",
    "mediators",
}


class JobOffer(DataAttribute):
    """Represents a job-offer object that inherits from DataAttribute."""

    def __init__(self):
        """Initializes a JobOffer object."""
        super().__init__()
        self.data_attributes = job_offer_attributes
