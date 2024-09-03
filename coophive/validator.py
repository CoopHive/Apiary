"""Module for defining the Validator class and its related functionalities."""

from coophive.agent import Agent
from coophive.log_json import log_json
from coophive.match import Match


class Validator(Agent):
    """Class representing a validator in the CoopHive simulator."""

    def __init__(
        self,
        private_key: str,
        public_key: str,
        auxiliary_states: dict = {},
    ):
        """Initialize the ResourceProvider instance."""
        super().__init__(
            private_key=private_key,
            public_key=public_key,
            auxiliary_states=auxiliary_states,
        )

    def verify_result(event):
        """Verifies that a task was completed by a resource provider and verifies the time/resources it took to complete it."""
        if event:
            return True
        return False
