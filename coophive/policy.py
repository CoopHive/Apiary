"""This module defines the Policy class used when agents, in general, make decisions within the CoopHive simulator."""


class Policy:
    """A policy in the Coophive simulator that defines the modes of behaviour of Agents with respect to the Schema.

    While the policy class is agnostic to the nature of the agent, because the action space is defined by the agent type,
    Specific policies are usable only by specific Agent types (e.g., Solvers and Clients have a different action space).
    """

    def __init__(self, policy_name):
        """Initialize a new Policy instance.

        Args:
            policy_name (str): The name of the policy.
        """
        self.policy_name = policy_name

    def train():
        """Train the policy function using stastistical learning techniques."""
        raise NotImplementedError

    def infer(self, match, states):
        """Evaluate the policy, following the (message, context) => message structure, and compute the message to be returned."""
        # TODO: policies shall act against message (here called match) and context (that I would call State). Fix API.
        if self.policy_name == "naive_accepter" and states:
            return ("accept", None)
        elif self.policy_name == "naive_rejecter" and states:
            return ("reject", None)
        elif self.policy_name == "identity_negotiator" and states:
            # TODO: return an actual counteroffer
            counteroffer = match
            return ("negotiate", counteroffer)
        else:
            return ("invalid policy or missing states", None)
