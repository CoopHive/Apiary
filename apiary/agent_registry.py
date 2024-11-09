"""Registry of Agents."""

import os

from apiary import buyer, seller, shared

agents_registry = {
    # ---------------------------------------------Buyers----------------------------------------------
    "buyer_naive": buyer.Naive,
    "buyer_kalman": lambda: shared.Kalman(is_buyer=True),
    "buyer_poly_time": lambda: shared.Time(is_buyer=True, alpha="poly"),
    "buyer_exp_time": lambda: shared.Time(is_buyer=True, alpha="exp"),
    # ---------------------------------------------Sellers---------------------------------------------
    "seller_naive": seller.Naive,
    "seller_kalman": lambda: shared.Kalman(is_buyer=False),
    "seller_poly_time": lambda: shared.Time(is_buyer=False, alpha="poly"),
    "seller_exp_time": lambda: shared.Time(is_buyer=False, alpha="exp"),
}


def get_agent():
    """Get agent from registry."""
    agent_name = os.getenv("AGENT_NAME")

    agent_class = agents_registry.get(agent_name)

    if agent_class is None:
        raise ValueError(f"Unknown agent: {agent_name}")

    return agent_class()
