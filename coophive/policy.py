"""This module defines the Policy class used when agents, in general, make decisions within the CoopHive simulator."""


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

    def __init__(self, policy_name):
        """Initialize a new Policy instance.

        Args:
            policy_name (str): The name of the policy.
        """
        self.policy_name = policy_name

    def train():
        """Train the policy function using stastistical learning techniques."""
        raise NotImplementedError

    def infer(self, match, localInformation):
        """Evaluate the policy, following the (message, context) => message structure, and compute the message to be returned."""
        # TODO: policies shall act against message (here called match) and context (that I would call State). Fix API.

        if self.policy_name == "naive_accepter":
            return "accept", None
        elif self.policy_name == "naive_rejecter":
            return "reject", None
        elif self.policy_name == "identity_negotiator":
            counteroffer = match
            return "negotiate", counteroffer
