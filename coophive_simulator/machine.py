"""This module defines the Machine class, which inherits from DataAttribute.

It provides functionality to manage machine attributes and generate unique machine UUIDs.
"""

from coophive_simulator.data_attribute import DataAttribute

machine_attributes = {"CPU", "RAM", "GPU", "created_at", "timeout"}


class Machine(DataAttribute):
    """Represents a machine with specific attributes and a unique UUID."""

    static_uuid = 0

    def __init__(self):
        """Initialize the machine with default attributes and a unique UUID."""
        super().__init__()
        self.data_attributes = machine_attributes
        # set machine uuid
        self.uuid = Machine.static_uuid
        # increment universal uuid counter
        Machine.static_uuid += 1

    def get_machine_uuid(self):
        """Return the unique UUID of the machine."""
        return self.uuid
