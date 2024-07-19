"""Define the Deal class which extends DataAttribute."""

from coophive_simulator.data_attribute import DataAttribute

# TODO: add "job" to deal attributes
deal_attributes = {
    "resource_provider_address",
    "client_address",
    "resource_offer",
    "job_offer",
    "price_per_instruction",
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
