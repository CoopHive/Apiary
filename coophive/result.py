"""Define the Result class which extends DataAttribute."""

from coophive.data_attribute import DataAttribute

result_attributes = {
    "deal_id",
    "result_id",
    "instruction_count",
}


class Result(DataAttribute):
    """Result class to handle specific data attributes related to results."""

    def __init__(self):
        """Initialize a new Result instance."""
        super().__init__()
        self.data_attributes = result_attributes

    def set_attributes(self, attributes):
        """Set attributes."""
        for key, value in attributes.items():
            if hasattr(self, key) or key in self.data_attributes:
                setattr(self, key, value)
