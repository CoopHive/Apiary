"""Agent Module."""

import logging
import os
from abc import ABC, abstractmethod

from dotenv import load_dotenv
from lighthouseweb3 import Lighthouse

load_dotenv()


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
    def __init__(self) -> None:
        """Initialize the Agent."""
        ...

    def start_agent_daemon(self):
        """Module responsible for launching daemons to make states accessible at inference time.

        e.g. launching postgrass. This won't perform heavy retraining operations nor
        trigger datapipelines to bring states up-to-date,
        but can take care of and updates cached states.
        """
        pass

    def stop_agent_daemon(self):
        """Check if we own the daemon process and stop it if so.

        In the presence of a parallel training process running it might not be the case.
        Daemon ownership is communicated via lock files.
        """
        pass

    def load_states(self):
        """Load necessary states in order to be able to perform an inference against incoming messages.

        This function includes the loading of models/policies parametrizations. Note that it is not responsibility of the agent
        to define the states, load them, train models on them to define policies. This function assumes the presence of
        a dataset of states to be loaded.
        """
        pass

    @abstractmethod
    def infer(self, states, input_message):
        """Infer scheme-compliant message following the (message, context) => message structure."""
        ...

    def _preprocess_infer(self, input_message):
        """Shared preprocessing logic for infer."""
        pubkey = os.getenv("PUBLIC_KEY")
        # if transmitter same as receiver:
        if input_message.get("pubkey") == pubkey:
            return "noop"

        # Initialize the output message
        output_message = input_message.copy()
        output_message["pubkey"] = pubkey
        output_message["initial"] = False

        return output_message

    def _get_query_cid(self, input_message):
        """Parse Dockerfile from input_message query, upload to IPFS and return the query_cid."""
        file_path = "tmp_lighthouse.Dockerfile"

        with open(file_path, "w") as file:
            file.write(input_message["data"]["query"])

        lh = Lighthouse(os.getenv("LIGHTHOUSE_TOKEN"))
        try:
            response = lh.upload(file_path)
            query_cid = response["data"]["Hash"]
        except Exception:
            logging.error("Lighthouse Error occurred.", exc_info=True)
            raise
        finally:
            # Remove the temporary file
            if os.path.exists(file_path):
                os.remove(file_path)

        logging.info(f"https://gateway.lighthouse.storage/ipfs/{query_cid}")
        return query_cid

    # TODO:
    # seller respond to buyer's attestation (payment) with their own attestation (result). Implement this in superclass and set variables from environment to self.x if useful.
    # uses: apiars.get_buy_statement()
    # Performs job.
    # uses: apiars.submit_and_collect()

    # TODO:
    # buyer receiving sell_attestations perform get_result_cid_from_sell_uid.


# TODO: understand if the inference agent is at least responsible for writing messages.
# Use message_timestamp to populate a database of messages?
# import time
# message_timestamp = int(time.time() * 1000)
