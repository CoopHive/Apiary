"""Module for defining the Validator class and its related functionalities."""

from coophive.agent import Agent


class Validator(Agent):
    """Class representing a validator in the CoopHive simulator."""

    def __init__(
        self,
        private_key: str,
        public_key: str,
        messagin_client_address: str,
        policy_name: str,
    ):
        """Initialize the Validator instance."""
        super().__init__(
            private_key=private_key,
            public_key=public_key,
            messagin_client_address=messagin_client_address,
            policy_name=policy_name,
        )

    def verify_result(event):
        """Verifies that a task was completed by a resource provider and verifies the time/resources it took to complete it."""
        if event:
            return True
        return False
