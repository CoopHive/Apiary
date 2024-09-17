"""This module defines the Policy class used when agents, in general, make decisions within the CoopHive simulator."""

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

    def infer(self, input_message: dict):
        """Evaluate the policy, following the (message, context) => message structure, and compute the message to be returned.

        Context/states are loaded here, only if necessary.
        """
        # if transmitter same as receiver:
        if input_message.get("pubkey") == self.public_key:
            return "noop"

        # TODO: as a function of the game being played, specificed as a mandatory input to the Agents API,
        # initialize the entries of the scheme which are inviariant across jobs. For example, the private key is constant.
        # if you are a seller, the offerId reply is the same as the incoming one..other entries of the scheme for different games
        # could have the same property. Make use of them to avoid thrivial computation at inference time/to avoid scheme-agnostic capabilities.
        # TODO: policies shall be able to conclude any negotiation: they need to "have an answer for every possible question"
        output_message = input_message.copy()
        output_message["pubkey"] = self.public_key
        output_message["initial"] = False
        if self.policy_name == "compute_marketplace_naive_rejecter":
            output_message["data"] = {"_tag": "cancel"}
        elif self.policy_name == "compute_marketplace_naive_accepter":
            raise NotImplementedError(self.policy_name)
        elif self.policy_name == "compute_marketplace_identity_negotiator":
            pass
        elif self.policy_name == "compute_marketplace_useless_state_loader":
            context = self.load_states()
            raise NotImplementedError(self.policy_name)
        else:
            raise NotImplementedError(f"Policy {self.policy_name} is not implemented.")

        # TODO: something akin to the following for agents to dump messages:
        # logging.info("Received response from server")
        # log_json(
        #     "Received response from server",
        #     {"response_message": response_message},
        # )

        # # TODO: transfer functionality inside policy evaluation
        # def negotiate_match(self, match, max_rounds=5):
        #     """Negotiate a match."""
        #     match_dict = match.get_data()
        #     rounds_completed = match_dict["rounds_completed"]
        #     while rounds_completed < max_rounds:
        #         new_match_offer = self.create_new_match_offer(match)
        #         response = self.communicate_request_to_party(new_match_offer)
        #         if response["accepted"]:
        #             self._agree_to_match(response["match_offer"])
        #             return
        #         match = response["counter_offer"]
        #         rounds_completed += 1
        #         match.set_attributes({"rounds_completed": rounds_completed})
        #     self.reject_match(match)

        return output_message
