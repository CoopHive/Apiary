"""Agent Module."""

import logging
import os
import subprocess
from abc import ABC, abstractmethod
from datetime import datetime

from dotenv import load_dotenv
from lighthouseweb3 import Lighthouse

from apiary import apiars

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
        # NOTE:
        # check that states (including p (internal states/model states/policy configurations))
        # are up to date and warning if not (not doing anything directly, another process is responsibile for doing something about it).
        #     import jax
        #     model_pickle = read_pickle('jax_model.pickle')
        #     model = jax.from_pickle(model_pickle) # This is why we do this in python, even if the training is happening in a completely separate process.
        #     return {'X': , ''}
        #    NOTE: in the case messaging is server-push-based, deal negotiations and job runs are necessarily sequential.
        pass

    def infer(self, states, input):
        """Infer scheme-compliant message following the (message, context) => message structure and populate negotiation thread."""
        output = self._preprocess_infer(input)
        if output == "noop":
            return output

        if input["initial"]:
            # Initial Offer UNIX time (Seller Measurement): negotiation thread t0.
            utc_time = datetime.utcnow().timestamp()
            os.environ["T0"] = str(utc_time)

        match input["data"].get("_tag"):
            case "offer":
                return self._handle_offer(input, output)
            case "buyAttest":
                return self._buy_attestation_to_sell_attestation(input, output)
            case "sellAttest":
                self._handle_sell_attestation(input)
                return "noop"

        return output

    def _preprocess_infer(self, input):
        """Shared preprocessing logic for infer."""
        pubkey = os.getenv("PUBLIC_KEY")
        # if transmitter same as receiver:
        if input.get("pubkey") == pubkey:
            return "noop"

        # Initialize the output message
        output = input.copy()
        output["pubkey"] = pubkey
        output["initial"] = False

        return output

    @abstractmethod
    def _handle_offer(self, input, output):
        """Handle offer messages."""
        ...

    def _buy_attestation_to_sell_attestation(self, input, output):
        statement_uid = input["data"]["attestation"]

        buy_statement = apiars.erc.get_buy_statement(statement_uid)

        if isinstance(buy_statement, apiars.erc.BuyStatement.ERC20):
            (_, _, _, job_cid) = buy_statement
            token_standard = "ERC20"
        elif isinstance(buy_statement, apiars.erc.BuyStatement.ERC721):
            (_, _, _, job_cid) = buy_statement
            token_standard = "ERC721"
        elif isinstance(buy_statement, apiars.erc.BuyStatement.Bundle):
            (_, _, _, _, _, job_cid) = buy_statement
            token_standard = "Bundle"

        result_cid = self._job_cid_to_result_cid(statement_uid, job_cid)

        match token_standard:
            case "ERC20":
                sell_uid = apiars.erc20.submit_and_collect(
                    statement_uid, result_cid, self.private_key
                )
            case "ERC721":
                sell_uid = apiars.erc721.submit_and_collect(
                    statement_uid, result_cid, self.private_key
                )
            case "Bundle":
                sell_uid = apiars.bundle.submit_and_collect(
                    statement_uid, result_cid, self.private_key
                )

        output["data"]["_tag"] = "sellAttest"
        output["data"]["attestation"] = sell_uid

        return output

    def _handle_sell_attestation(self, input):
        sell_uid = input["data"]["attestation"]
        result_cid = apiars.erc.get_sell_statement(sell_uid)
        self._get_result_from_result_cid(result_cid)

    def _get_query(self, input):
        """Parse Dockerfile from input query, upload to IPFS and return the query."""
        file_path = "tmp_lighthouse.Dockerfile"

        with open(file_path, "w") as file:
            file.write(input["data"]["query"])

        try:
            response = self.lh.upload(file_path)
            query = response["data"]["Hash"]
        except Exception:
            logging.error("Lighthouse Error occurred.", exc_info=True)
            raise
        finally:
            # Remove the temporary file
            if os.path.exists(file_path):
                os.remove(file_path)

        logging.info(f"https://gateway.lighthouse.storage/ipfs/{query}")
        return query

    def _offer_to_buy_attestation(self, input, output):
        query = self._get_query(input)

        if len(input["data"]["tokens"]) == 1:
            input_token = input["data"]["tokens"][0]

            token_standard = str(input_token["tokenStandard"])
            token_address = str(input_token["address"])

            if token_standard == "ERC20":
                amount = int(input_token["amt"])

                statement_uid = apiars.erc20.make_buy_statement(
                    token_address, amount, query, self.private_key
                )
            elif token_standard == "ERC721":
                token_id = int(input_token["id"])
                statement_uid = apiars.erc721.make_buy_statement(
                    token_address, token_id, query, self.private_key
                )
        else:
            tokens = input["data"]["tokens"]

            erc20_list = [
                token for token in tokens if token["tokenStandard"] == "ERC20"
            ]

            erc20_addresses_list = [
                erc20_token["address"] for erc20_token in erc20_list
            ]
            erc20_amounts_list = [erc20_token["amt"] for erc20_token in erc20_list]

            erc721_list = [
                token for token in tokens if token["tokenStandard"] == "ERC721"
            ]

            erc721_addresses_list = [
                erc721_token["address"] for erc721_token in erc721_list
            ]
            erc721_ids_list = [erc721_token["id"] for erc721_token in erc721_list]

            statement_uid = apiars.bundle.make_buy_statement(
                erc20_addresses_list,
                erc20_amounts_list,
                erc721_addresses_list,
                erc721_ids_list,
                query,
                self.private_key,
            )

        output["data"]["_tag"] = "buyAttest"
        output["data"]["attestation"] = statement_uid
        output["data"].pop("query", None)
        output["data"].pop("tokens", None)

        return output

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

        # Build the image
        build_command = f"podman build -t job-image-{statement_uid} tmp"
        subprocess.run(build_command, shell=True, check=True)

        # Run the container and capture the output
        run_command = f"podman run --name job-container-{
            statement_uid} job-image-{statement_uid}"
        result = subprocess.run(
            run_command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
        )

        # TODO: make result generic to volume.
        result = result.stdout

        # Remove the container
        remove_command = f"podman rm job-container-{statement_uid}"
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
