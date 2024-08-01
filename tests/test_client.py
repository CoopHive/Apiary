from unittest.mock import MagicMock

import pytest

from coophive.client import Client
from coophive.deal import Deal
from coophive.event import Event
from coophive.job import Job
from coophive.match import Match
from coophive.result import Result
from coophive.smart_contract import SmartContract
from coophive.solver import Solver
from coophive.utils import Tx


@pytest.fixture
def setup_client():
    """Fixture to set up the test environment."""
    client = Client(address="client_key")
    smart_contract = SmartContract(public_key="smart_contract_key")
    client.get_smart_contract = lambda: smart_contract
    match = Match()
    smart_contract.balances = {"client_key": 1000, "resource_key": 500}
    client._create_transaction = lambda value: Tx(
        sender=client.get_public_key(), value=value
    )
    return client, smart_contract, match


def test_get_solver(setup_client):
    """Test the get_solver method."""
    client, _, _ = setup_client
    solver = Solver(public_key="solver_key", url="http://solver.com")
    client.connect_to_solver(url="http://solver.com", solver=solver)
    assert client.get_solver() == solver
