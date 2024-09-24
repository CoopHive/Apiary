"""Agent Module."""

from abc import ABC, abstractmethod

agents = {"buyer": str, "seller": str}


def get_agent(config):
    """Get agent from config."""
    config.agent.role
    pass


class Agent(ABC):
    """A class to represent an Agent.

    Agents are entities such as Buyers, Sellers and Validators.

    Agents are characterized by three families of actions:
        - Participate in Negotiations: receiving messages, combining it with additional context, using a policy, and generating an output
          scheme-compliant message.
        - Reading/writing on-chain states (e.g., attestations) in tandem with the finalization of a deal.
        - Performing the actual task being negotiated, after the handshake (e.g., running a docker-based compute job).

    The Agent inferences are designed to be stateless, meaning that their states are loaded at inference time rather than being stored in memory.
    The history of these states is managed externally via storage mechanisms like databases or flatfiles (e.g., PostgreSQL, .parquet).

    The responsibility for managing the history and updates of states (including feature definitions, pipelines, model parametrizations),
    if necessary, is separate.
    """

    @abstractmethod
    def __init__(self, config) -> None:
        """Initialize the Agent."""
        ...

    @abstractmethod
    def start_agent_daemon(self):
        """Module responsible for launching daemons to make states accessible at inference time.

        e.g. launching postgrass. This won't perform heavy retraining operations nor
        trigger datapipelines to bring states up-to-date,
        but can take care of and updates cached states.
        """
        ...

    @abstractmethod
    def stop_agent_daemon(self):
        """Check if we own the daemon process and stop it if so.

        In the presence of a parallel training process running it might not be the case.
        Daemon ownership is communicated via lock files.
        """
        ...

    @abstractmethod
    def load_states(self):
        """Load necessary states in order to be able to perform an inference against incoming messages.

        This function includes the loading of models/policies parametrizations. Note that it is not responsibility of the agent
        to define the states, load them, train models on them to define policies. This function assumes the presence of
        a dataset of states to be loaded.
        """
        # TODO:
        # check that states (including p (internal states/model states/policy configurations))
        # are up to date and warning if not (not doing anything directly, another process is responsibile for doing something about it).
        ...

    @abstractmethod
    def infer(self, states, input_message):
        """Infer scheme-compliant message from states and input_message."""
        # TODO:
        # use match to cover all the scheme-compliant cases:
        # https://github.com/CoopHive/redis-scheme-client/blob/main/src/compute-marketplace-scheme.ts#L19
        # define and import functions for cases in which the action is complex.
        ...
