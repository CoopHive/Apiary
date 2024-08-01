"""This state module defines the classes used represent all the on-chain variables."""


class Addresses:
    """A class to represent and manage addresses.

    These addresses are used to identify public addresses of clients and resource providers, smart contracts.
    """

    def __init__(self):
        """Initialize the Addresses class with a starting address."""
        self.current_address = 0

    def get_current_address(self):
        """Increment and get the current address as a string."""
        self.increment_current_address()
        return str(self.current_address)

    def increment_current_address(self):
        """Increment the current address counter by 1."""
        self.current_address += 1
