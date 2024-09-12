"""This module defines the Policy class used when agents, in general, make decisions within the CoopHive simulator."""

import pandas as pd


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

    def load_states(self):
        """Get the states for the agent policy to be trained/evaluated, if needed.

        States are loaded at training/inference time only.
        """
        auxiliary_states = pd.read_parquet(
            f"auxiliary_states_{self.policy_name}.parquet"
        )
        messaging_states = pd.read_parquet(
            f"messaging_states_{self.policy_name}.parquet"
        )
        policy_states = pd.read_parquet(f"policy_states_{self.policy_name}.parquet")
        return [auxiliary_states, messaging_states, policy_states]

    def train(self):
        """Train the policy function using stastistical learning techniques."""
        # TODO: load states here if necessary:
        # X = self.load_states()
        # because of the stateless nature, train is responsible fro loading auxiliary_states, messaging_states
        # and potentially (historical) policy_states and update the policy_states file.
        raise NotImplementedError(self.policy_name)

    def infer(self, message):
        """Evaluate the policy, following the (message, context) => message structure, and compute the message to be returned.

        Context/states are loaded here, if necessary.
        """
        if self.policy_name == "naive_accepter":
            # TODO: fix, this policy is not scheme compliant.
            return "accept"
        elif self.policy_name == "naive_rejecter":
            # TODO: fix, this policy is not scheme compliant.
            return "reject"
        elif self.policy_name == "identity_negotiator":
            # TODO: fix, this policy is not correct, even if scheme-compliant
            # as it uses the received message address, instead of the submitter.
            return message
        elif self.policy_name == "useless_state_loader":
            # TODO: fix, this policy is not scheme compliant.
            context = self.load_states()
            return "accept"
        else:
            raise NotImplementedError(f"Policy {self.policy_name} is not implemented.")
