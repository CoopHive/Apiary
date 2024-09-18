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

extra_necessary_match_data = {
    "buyer_deposit": 5,
    "timeout": 10,
    "timeout_deposit": 3,
    "cheating_collateral_multiplier": 50,
    "price_per_instruction": 1,
    "verification_method": "random",
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

    def sign_seller(self):
        """Set the seller signed flag to True."""
        self.seller_signed = True

    def sign_buyer(self):
        """Set the buyer signed flag to True."""
        self.buyer_signed = True
