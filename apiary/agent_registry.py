"""Registry of Agents."""

import os

from apiary import buyer, seller


def get_agent():
    """Get agent from registry."""
    agent_name = os.getenv("AGENT_NAME")

    agents = {
        "buyer_naive": buyer.NaiveBuyer,
        "seller_naive": seller.NaiveSeller,
        # Add more agents as needed
    }

    agent_class = agents.get(agent_name)

    if agent_class is None:
        raise ValueError(f"Unknown agent: {agent_name}")

    return agent_class()
