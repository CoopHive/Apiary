"""This module defines the Agents Shared among different roles, used within the CoopHive protocol."""

import json
import logging
import os
from datetime import datetime
from typing import Literal

import numpy as np
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
        self.abs_tol = float(os.getenv("ABSOLUTE_TOLERANCE") or 0.0)

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

        add_float_to_csv(input["data"]["tokens"][0]["amt"], "negotiation")
        valuation_estimation = float(os.getenv("VALUATION_ESTIMATION"))
        valuation_variance = float(os.getenv("VALUATION_VARIANCE"))

        valuation_measurement = input["data"]["tokens"][0]["amt"]

        if (
            self.is_buyer
            and valuation_measurement <= valuation_estimation + self.abs_tol
        ):
            # Beneficial incoming offer, no further negotiation needed.
            return self._offer_to_buy_attestation(input, output)
        elif not self.is_buyer and valuation_measurement >= valuation_estimation:
            # Beneficial incoming offer, no further negotiation needed.
            # Confirm buyer offer with identity counteroffer
            return output
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
            os.environ["VALUATION_ESTIMATION"] = str(valuation_estimation)
            output["data"]["tokens"][0]["amt"] = valuation_estimation

            add_float_to_csv(output["data"]["tokens"][0]["amt"], "negotiation")
            return output


class Time(Agent):
    """Time Dependent Agent in the CoopHive protocol."""

    def __init__(self, is_buyer: bool, alpha: Literal["poly", "exp"]) -> None:
        """Initialize the instance."""
        super().__init__()
        logging.info("Time initialized.")
        self.is_buyer = is_buyer
        self.alpha = alpha
        self.abs_tol = float(os.getenv("ABSOLUTE_TOLERANCE") or 0.0)

    def _poly(self, t, t_max, beta, k):
        return k + (1 - k) * (t / t_max) ** (1 / beta)

    def _exp(self, t, t_max, beta, k):
        return k ** ((1 - t / t_max) ** beta)

    def _handle_offer(self, input, output):
        """Handle Offer Using Time."""
        if (
            len(input["data"]["tokens"]) != 1
            or input["data"]["tokens"][0]["tokenStandard"] != "ERC20"
        ):
            raise ValueError(
                "Strategy currently defined over scalar ERC20 amount only."
            )
            # NOTE: Actually defined only for USDC, more in particular.
            # TODO: Agents shall have a whitelist of assets and potentially a set of parameters asset-specific, in the multivariate case.
            # This is true for every strategy, and should inform the high-level design of agents.

        t0 = float(os.getenv("T0"))
        t = datetime.utcnow().timestamp() - t0
        t_max = float(os.getenv("T_MAX"))

        if t > t_max:
            return "noop"

        add_float_to_csv(input["data"]["tokens"][0]["amt"], "negotiation")
        x_in = input["data"]["tokens"][0]["amt"]

        beta = float(os.getenv("BETA"))
        k = float(os.getenv("K"))

        if self.alpha == "poly":
            alpha_t = self._poly(t, t_max, beta, k)
        elif self.alpha == "exp":
            alpha_t = self._exp(t, t_max, beta, k)

        x_min = int(os.getenv("MIN_USDC"))
        x_max = int(os.getenv("MAX_USDC"))

        if self.is_buyer:
            x_out = x_min + alpha_t * (x_max - x_min)
        else:
            x_out = x_min + (1 - alpha_t) * (x_max - x_min)

        if self.is_buyer and x_in <= x_out + self.abs_tol:
            # Beneficial incoming offer, no further negotiation needed.
            return self._offer_to_buy_attestation(input, output)
        elif not self.is_buyer and x_in >= x_out:
            # Beneficial incoming offer, no further negotiation needed.
            # Confirm buyer offer with identity counteroffer
            return output
        else:
            output["data"]["tokens"][0]["amt"] = x_out
            add_float_to_csv(output["data"]["tokens"][0]["amt"], "negotiation")
            return output


class TitForTat(Agent):
    """TitForTat Agent in the CoopHive protocol."""

    def __init__(
        self,
        is_buyer: bool,
        imitation_type: Literal["relative", "random_absolute", "averaged"],
    ) -> None:
        """Initialize the instance."""
        super().__init__()
        logging.info("TitForTat initialized.")
        self.is_buyer = is_buyer
        self.imitation_type = imitation_type
        self.delta = int(os.getenv("DELTA"))
        self.abs_tol = float(os.getenv("ABSOLUTE_TOLERANCE") or 0.0)

    def _handle_offer(self, input, output):
        """Handle Offer."""
        if (
            len(input["data"]["tokens"]) != 1
            or input["data"]["tokens"][0]["tokenStandard"] != "ERC20"
        ):
            raise ValueError(
                "Strategy currently defined over scalar ERC20 amount only."
            )
            # NOTE: Actually defined only for USDC, more in particular.
            # TODO: Agents shall have a whitelist of assets and potentially a set of parameters asset-specific, in the multivariate case.
            # This is true for every strategy, and should inform the high-level design of agents.

        add_float_to_csv(input["data"]["tokens"][0]["amt"], "negotiation")
        x_in = input["data"]["tokens"][0]["amt"]

        x_int_t_str = "X_IN_T"
        x_in_t = json.loads(os.getenv(x_int_t_str, "[]"))
        x_in_t.append(x_in)
        os.environ[x_int_t_str] = json.dumps(x_in_t)

        x_min = float(os.getenv("MIN_USDC"))
        x_max = float(os.getenv("MAX_USDC"))

        len_x_in_t = len(x_in_t)
        if len_x_in_t < 2:
            x_out = x_min if self.is_buyer else x_max
        else:
            delta = min(len_x_in_t - 1, self.delta)
            last_x_out = float(os.getenv("X_OUT", 0))

            if self.imitation_type == "relative":
                ratio = x_in_t[-delta - 1] / x_in_t[-delta]
                x_out = min(max(ratio * last_x_out, x_min), x_max)
            elif self.imitation_type == "random_absolute":
                variation = x_in_t[-delta - 1] - x_in_t[-delta]
                perturbation = (
                    +(1 ** (int(self.is_buyer)))
                    * float(os.getenv("M", 1))
                    * np.random.randn() ** 2
                )
                x_out = min(max(last_x_out + variation + perturbation, x_min), x_max)
            elif self.imitation_type == "averaged":
                ratio = x_in_t[-delta - 1] / x_in_t[-1]
                x_out = min(max(ratio * last_x_out, x_min), x_max)

        os.environ["X_OUT"] = str(x_out)

        if self.is_buyer and x_in <= x_out + self.abs_tol:
            # Beneficial incoming offer, no further negotiation needed.
            return self._offer_to_buy_attestation(input, output)
        elif not self.is_buyer and x_in >= x_out:
            # Beneficial incoming offer, no further negotiation needed.
            # Confirm buyer offer with identity counteroffer
            return output
        else:
            output["data"]["tokens"][0]["amt"] = x_out
            add_float_to_csv(output["data"]["tokens"][0]["amt"], "negotiation")
            return output
