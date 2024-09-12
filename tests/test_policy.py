from unittest.mock import MagicMock, patch

import pytest

from coophive.client import Client
from coophive.match import Match
from coophive.policy import Policy
from coophive.resource_provider import ResourceProvider

private_key_client = (
    "0x4c0883a69102937d6231471b5dbb6204fe512961708279a4a6075d78d6d3721b"
)
private_key_resource = (
    "0x4c0883a69102937d6231471b5dbb6204fe512961708279a4a6075d78d6d3721c"
)
public_key_client = "0x627306090abaB3A6e1400e9345bC60c78a8BEf57"
public_key_resource = "0x627306090abaB3A6e1400e9345bC60c78a8BEf56"


@pytest.fixture
def setup_agents_with_policies():
    """Fixture to set up the test environment with agents and policies."""
    with (
        patch("socket.socket") as mock_socket,
        patch("docker.from_env") as mock_docker_from_env,
    ):
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Mock Docker client
        mock_docker_client = MagicMock()
        mock_docker_from_env.return_value = mock_docker_client

        policy_a = Policy("naive_accepter")
        policy_b = Policy("naive_rejecter")
        policy_c = Policy("identity_negotiator")

        client = Client(
            private_key=private_key_client,
            public_key=public_key_client,
            policy=policy_a,
        )

        resource_provider = ResourceProvider(
            private_key=private_key_resource,
            public_key=public_key_resource,
            policy=policy_b,
        )

        return client, resource_provider, policy_c


def test_make_match_decision_with_policies(setup_agents_with_policies):
    """Test the make_match_decision method with different policies."""
    client, resource_provider, policy_c = setup_agents_with_policies

    mock_match = Match()
    mock_match.set_attributes(
        {
            "client_address": "client_address",
            "resource_provider_address": "resource_provider_address",
            "client_deposit": 100,
            "price_per_instruction": 10,
            "expected_number_of_instructions": 1000,
        }
    )

    client._agree_to_match = MagicMock()
    client.make_match_decision(mock_match)
    client._agree_to_match.assert_called_once_with(mock_match)

    resource_provider.reject_match = MagicMock()
    resource_provider.make_match_decision(mock_match)
    resource_provider.reject_match.assert_called_once_with(mock_match)

    client.policy = policy_c
    client.negotiate_match = MagicMock()
    client.make_match_decision(mock_match)
    client.negotiate_match.assert_called_once_with(mock_match)

    client._agree_to_match.reset_mock()
    resource_provider.reject_match.reset_mock()
    client.negotiate_match.reset_mock()

    def mock_infer(message):
        return "accept"

    client.policy.infer = MagicMock(side_effect=mock_infer)

    client.make_match_decision(mock_match)

    client.policy.infer.assert_called_once()
    client._agree_to_match.assert_called_once_with(mock_match)


if __name__ == "__main__":
    pytest.main()
