"""Agent Module."""

import logging
import os
import subprocess
from abc import ABC, abstractmethod

from dotenv import load_dotenv
from lighthouseweb3 import Lighthouse

load_dotenv(override=True)


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

    def __init__(self) -> None:
        """Initialize the Agent."""
        self.private_key = os.getenv("PRIVATE_KEY")
        self.lh = Lighthouse(os.getenv("LIGHTHOUSE_TOKEN"))

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

        try:
            response = self.lh.upload(file_path)
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

    def _job_cid_to_result_cid(self, statement_uid: str, job_cid: str):
        """Download Dockerfile from job_cid, run the job, upload the results to IPFS and return the result_cid."""
        try:
            dockerFile = self.lh.download(job_cid)
        except Exception:
            logging.error("Lighthouse Error occurred.", exc_info=True)
            raise

        if not os.path.exists("tmp"):
            os.makedirs("tmp")

        # Write Dockerfile
        with open("tmp/Dockerfile", "w") as f:
            f.write(dockerFile[0].decode("utf-8"))

        # Build the Docker image
        build_command = f"docker build -t job-image-{statement_uid} tmp"
        subprocess.run(build_command, shell=True, check=True)

        # Run the Docker container and capture the output
        run_command = (
            f"docker run --name job-container-{statement_uid} job-image-{statement_uid}"
        )
        result = subprocess.run(
            run_command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
        )
        result = result.stdout

        # Remove the Docker container
        remove_command = f"docker rm job-container-{statement_uid}"
        subprocess.run(remove_command, shell=True, check=True)

        result_file = "tmp/output.txt"
        with open(result_file, "w") as file:
            # Write the variable to the file
            file.write(result)

        try:
            response = self.lh.upload(result_file)
        except Exception:
            logging.error("Lighthouse Error occurred.", exc_info=True)
            raise

        result_cid = response["data"]["Hash"]
        return result_cid

    def _get_result_from_result_cid(self, result_cid):
        try:
            results = self.lh.download(result_cid)
        except Exception:
            logging.error("Lighthouse Error occurred.", exc_info=True)
            raise

        if not os.path.exists("results/"):
            os.makedirs("results")

        # Write Dockerfile
        with open(f"results/{result_cid}.txt", "w") as f:
            f.write(results[0].decode("utf-8"))


# TODO: understand if the inference agent is at least responsible for writing messages.
# Use message_timestamp to populate a database of messages?
# import time
# message_timestamp = int(time.time() * 1000)
