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
    return Policy("naive_accepter")


@pytest.fixture
def agent_public_key():
    return "0xabcdef123456789"


@pytest.fixture
def auxiliary_states():
    return {"state_1": "value_1", "state_2": "value_2"}


@pytest.fixture
def agent(setup_private_key, agent_public_key, agent_policy, auxiliary_states):
    return Agent(
        private_key=setup_private_key,
        public_key=agent_public_key,
        policy=agent_policy,
        auxiliary_states=auxiliary_states,
    )


def test_agent_initialization(
    agent, setup_private_key, agent_public_key, agent_policy, auxiliary_states
):
    assert agent.private_key == setup_private_key
    assert agent.public_key == agent_public_key
    assert agent.policy == agent_policy
    assert isinstance(agent.auxiliary_states, dict)
    assert agent.auxiliary_states == auxiliary_states


if __name__ == "__main__":
    pytest.main()
