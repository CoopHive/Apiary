"""Define the Deal class which extends DataAttribute."""

from coophive.data_attribute import DataAttribute

deal_attributes = {
    "seller_address",
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
