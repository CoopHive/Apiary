from unittest.mock import MagicMock, patch

import docker
import pytest
from coophive.client import Client
from coophive.match import Match
from coophive.policy import Policy
from coophive.resource_provider import ResourceProvider


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

        policy_a = Policy("a")
        policy_b = Policy("b")
        policy_c = Policy("c")

        client = Client("client_address", policy_a)
        resource_provider = ResourceProvider("resource_provider_address", policy_b)

        return client, resource_provider, policy_c


def test_make_match_decision_with_policies(setup_agents_with_policies):
    """Test the make_match_decision method with different policies."""
    client, resource_provider, policy_c = setup_agents_with_policies

    # Create a mock Match object
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

    # Test Client with Policy 'a' (always accept)
    client._agree_to_match = MagicMock()
    client.make_match_decision(mock_match)
    client._agree_to_match.assert_called_once_with(mock_match)

    # Test ResourceProvider with Policy 'b' (always reject)
    resource_provider.reject_match = MagicMock()
    resource_provider.make_match_decision(mock_match)
    resource_provider.reject_match.assert_called_once_with(mock_match)

    # Test with Policy 'c' (always negotiate)
    client.policy = policy_c
    client.negotiate_match = MagicMock()
    client.make_match_decision(mock_match)
    client.negotiate_match.assert_called_once_with(mock_match)

    # Reset mocks
    client._agree_to_match.reset_mock()
    resource_provider.reject_match.reset_mock()
    client.negotiate_match.reset_mock()

    # Test that local information is passed to policy
    def mock_make_decision(match, local_info):
        assert local_info == {"some": "info"}
        return "accept", None

    client.policy.make_decision = MagicMock(side_effect=mock_make_decision)
    client.get_local_information = MagicMock(return_value={"some": "info"})

    client.make_match_decision(mock_match)

    client.policy.make_decision.assert_called_once()
    client.get_local_information.assert_called_once()
    client._agree_to_match.assert_called_once_with(mock_match)


if __name__ == "__main__":
    pytest.main()
