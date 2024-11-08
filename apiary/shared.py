"""This module defines the Agents Shared among different roles, used within the CoopHive protocol."""

import logging
import os
from datetime import datetime
from typing import Literal

from apiary.base_agent import Agent
from apiary.utils import add_float_to_csv
from dotenv import load_dotenv

load_dotenv(override=True)


class Kalman(Agent):
    """Kalman filter-based Agent in the CoopHive protocol."""

    def __init__(self, is_buyer: bool) -> None:
        """Initialize the instance."""
        super().__init__()
        logging.info("Kalman initialized.")
        self.is_buyer = is_buyer

    def _handle_offer(self, input, output):
        # TODO: generalize strategy to multi-dimensional payment case.

        # TODO: move to appending the state of the negotiation instead of overwriting it
        # (which would end up using messaging_thread[-1] as input only for the current strategy),
        # to generalize the dynamics (time-delay embedding, Takens's theorem...).

        if (
            len(input["data"]["tokens"]) != 1
            or input["data"]["tokens"][0]["tokenStandard"] != "ERC20"
        ):
            raise ValueError(
                "Strategy currently defined over scalar ERC20 amount only."
            )

        valuation_estimation = float(os.getenv("VALUATION_ESTIMATION") or 300.0)
        valuation_variance = float(os.getenv("VALUATION_VARIANCE") or 10.0)
        abs_tol = float(os.getenv("ABSOLUTE_TOLERANCE") or 0.0)

        valuation_measurement = input["data"]["tokens"][0]["amt"]

        if not self.is_buyer:
            add_float_to_csv(valuation_estimation)
            add_float_to_csv(valuation_measurement)

        if self.is_buyer and valuation_measurement <= valuation_estimation + abs_tol:
            # Beneficial incoming offer, no further negotiation needed.
            output = self._offer_to_buy_attestation(input, output)
        elif not self.is_buyer and valuation_measurement >= valuation_estimation:
            # Beneficial incoming offer, no further negotiation needed.
            # Confirm buyer offer with identity counteroffer
            pass
        else:
            valuation_measurement_variance = float(
                os.getenv("VALUATION_MEASUREMENT_VARIANCE")
            )

            kalman_gain = valuation_variance / (
                valuation_variance + valuation_measurement_variance
            )

            # Covariance Update
            valuation_variance *= 1 - kalman_gain
            os.environ["VALUATION_VARIANCE"] = str(valuation_variance)

            # State Update
            valuation_estimation *= 1 - kalman_gain
            valuation_estimation += kalman_gain * valuation_measurement
            valuation_estimation = round(
                valuation_estimation
            )  # EVM-compatible integer.
            os.environ["VALUATION_ESTIMATION"] = str(valuation_estimation)
            output["data"]["tokens"][0]["amt"] = valuation_estimation

        return output


class Time(Agent):
    """Time Dependent Agent in the CoopHive protocol."""

    def __init__(self, is_buyer: bool, alpha_t: Literal["poly", "exp"]) -> None:
        """Initialize the instance."""
        super().__init__()
        logging.info("Kalman initialized.")
        self.is_buyer = is_buyer
        self.alpha_t = alpha_t

    def _handle_offer(self, input, output):
        """Handle Offer Using Time."""
        utc_time = datetime.utcnow().timestamp()
        t = utc_time - int(os.getenv("t0"))

        print(t)
        1 / 0

        if (
            len(input["data"]["tokens"]) != 1
            or input["data"]["tokens"][0]["tokenStandard"] != "ERC20"
        ):
            raise ValueError(
                "Strategy currently defined over scalar ERC20 amount only."
            )
            # NOTE: Actually defined only for USDC, more in particular.
            # TODO: Agents shall have a whitelist of assets and potentially a set of parameters asset-specific, in the multivariate case.
            # This is true for every strategy, and should inform the design.
