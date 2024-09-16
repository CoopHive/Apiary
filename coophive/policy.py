"""This module defines the Policy class used when agents, in general, make decisions within the CoopHive simulator."""

import json

import pandas as pd


class Policy:
    """Defines the behavior of Agents based on a predefined policy within the CoopHive simulator.

    Policies dictate how an Agent interacts with the Schema-compliant messaging scheme (action space), determining its mode of behavior.
    Each policy operates in a stateless manner, meaning that the Agent's actions (inferences) are computed in real-time
    using the current state, without persisting any state in memory.

    While the policy class is agnostic to the nature of the agent, because the action space is defined by the agent type,
    Specific policies are usable only by specific Agent types (e.g., Solvers and Clients have a different action space).

    Policy States:
        - Policies are dynamically updated through machine learning models, with the responsibility on the Agent
          to load the relevant state at inference time.

    Messages:
        - The Agent loads messages from an external Redis or database for stateless messaging, ensuring real-time responses.

    Environmental States:
        - These states represent external factors affecting the Agent and are loaded from external data pipelines
          or off-chain sources.

    Args:
        policy_name (str): The name of the policy used by the Agent. Policy types can dictate different behaviors,
        such as accepting all offers (naive_accepter), rejecting all offers (naive_rejecter), or negotiating terms (identity_negotiator).

    Methods:
        train: This method is used to train the policy using statistical learning techniques.
        infer: Evaluate the current state and return an action/message based on the loaded state and policy.
    """

    def __init__(self, public_key: str, policy_name: str):
        """Initialize a new Policy instance."""
        self.public_key = public_key
        self.policy_name = policy_name

    # TODO: make this loading more modular.
    # some policies may train on the auxiliary states history only,
    # others on a combination.
    def load_states(self):
        """Get the states for the agent policy to be trained/evaluated, if needed.

        States are (optionally) loaded at training/inference time only.
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
        if (
            json.loads(message).get("pubkey") == self.public_key
        ):  # if transmitter same as receiver
            return "noop"

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
