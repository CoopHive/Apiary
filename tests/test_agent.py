import os

import pytest

from coophive.agent import Agent
from coophive.policy import Policy


@pytest.fixture
def setup_private_key(monkeypatch):
    monkeypatch.setenv("PRIVATE_KEY", "0x123456789abcdef")
    return os.environ["PRIVATE_KEY"]


@pytest.fixture
def agent_policy():
    return "naive_accepter"


@pytest.fixture
def agent_public_key():
    return "0xabcdef123456789"


@pytest.fixture
def agent(setup_private_key, agent_public_key, agent_policy):
    return Agent(
        private_key=setup_private_key,
        public_key=agent_public_key,
        policy_name=agent_policy,
    )


def test_agent_initialization(agent, setup_private_key, agent_public_key):
    assert agent.private_key == setup_private_key
    assert agent.public_key == agent_public_key
    assert isinstance(agent.policy, Policy)


if __name__ == "__main__":
    pytest.main()
