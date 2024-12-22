import os

import pytest
from apiary.agent_registry import get_agent

from apiary import buyer, seller, shared

os.environ["LIGHTHOUSE_TOKEN"] = "tmp"


# Test case to check if the agent is returned correctly for a known buyer
def test_get_buyer_naive():
    os.environ["AGENT_NAME"] = "buyer_naive"
    agent = get_agent()
    assert isinstance(agent, buyer.Naive)


# Test case to check if the agent is returned correctly for a known seller
def test_get_seller_naive():
    os.environ["AGENT_NAME"] = "seller_naive"
    agent = get_agent()
    assert isinstance(agent, seller.Naive)


# Test case to check if the agent is returned correctly for a buyer with Kalman
def test_get_buyer_kalman():
    os.environ["AGENT_NAME"] = "buyer_kalman"
    agent = get_agent()
    assert isinstance(agent, shared.Kalman)
    assert agent.is_buyer is True


# Test case to check if the agent is returned correctly for a seller with Kalman
def test_get_seller_kalman():
    os.environ["AGENT_NAME"] = "seller_kalman"
    agent = get_agent()
    assert isinstance(agent, shared.Kalman)
    assert agent.is_buyer is False


# Test case to check if the agent is returned correctly for buyer with Time (poly)
def test_get_buyer_poly_time():
    os.environ["AGENT_NAME"] = "buyer_poly_time"
    agent = get_agent()
    assert isinstance(agent, shared.Time)
    assert agent.is_buyer is True
    assert agent.alpha == "poly"


# Test case to check if the agent is returned correctly for seller with Time (poly)
def test_get_seller_poly_time():
    os.environ["AGENT_NAME"] = "seller_poly_time"
    agent = get_agent()
    assert isinstance(agent, shared.Time)
    assert agent.is_buyer is False
    assert agent.alpha == "poly"


# Test case to check if the agent is returned correctly for buyer with Time (exp)
def test_get_buyer_exp_time():
    os.environ["AGENT_NAME"] = "buyer_exp_time"
    agent = get_agent()
    assert isinstance(agent, shared.Time)
    assert agent.is_buyer is True
    assert agent.alpha == "exp"


# Test case to check if the agent is returned correctly for seller with Time (exp)
def test_get_seller_exp_time():
    os.environ["AGENT_NAME"] = "seller_exp_time"
    agent = get_agent()
    assert isinstance(agent, shared.Time)
    assert agent.is_buyer is False
    assert agent.alpha == "exp"


# Test case to check if the agent is returned correctly for buyer with TitForTat
def test_get_buyer_tit_for_tat():
    os.environ["AGENT_NAME"] = "buyer_tit_for_tat"
    os.environ["IMITATION_TYPE"] = "some_type"
    os.environ["DELTA"] = "1"
    agent = get_agent()
    assert isinstance(agent, shared.TitForTat)
    assert agent.is_buyer is True
    assert agent.imitation_type == "some_type"


# Test case to check if the agent is returned correctly for seller with TitForTat
def test_get_seller_tit_for_tat():
    os.environ["AGENT_NAME"] = "seller_tit_for_tat"
    os.environ["IMITATION_TYPE"] = "some_type"
    os.environ["DELTA"] = "1"
    agent = get_agent()
    assert isinstance(agent, shared.TitForTat)
    assert agent.is_buyer is False
    assert agent.imitation_type == "some_type"


# Test case to check if an unknown agent name raises an error
def test_get_unknown_agent():
    os.environ["AGENT_NAME"] = "unknown_agent"
    with pytest.raises(ValueError, match="Unknown agent: unknown_agent"):
        get_agent()
