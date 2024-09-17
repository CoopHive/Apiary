from unittest.mock import MagicMock, patch

import pytest

from coophive.buyer import Buyer
from coophive.policy import Policy
from coophive.seller import Seller

private_key_buyer = "0x4c0883a69102937d6231471b5dbb6204fe512961708279a4a6075d78d6d3721b"
private_key_seller = (
    "0x4c0883a69102937d6231471b5dbb6204fe512961708279a4a6075d78d6d3721c"
)
public_key_buyer = "0x627306090abaB3A6e1400e9345bC60c78a8BEf57"
public_key_seller = "0x627306090abaB3A6e1400e9345bC60c78a8BEf56"


@pytest.fixture
def setup_agents_with_policies():
    """Fixture to set up the test environment with agents and policies."""
    with (
        patch("socket.socket") as mock_socket,
        patch("docker.from_env") as mock_docker_from_env,
    ):
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Mock Docker buyer
        mock_docker_buyer = MagicMock()
        mock_docker_from_env.return_value = mock_docker_buyer

        policy_a = "naive_accepter"
        policy_b = "naive_rejecter"
        policy_c = "identity_negotiator"

        buyer = Buyer(
            private_key=private_key_buyer,
            public_key=public_key_buyer,
            policy_name=policy_a,
        )

        seller = Seller(
            private_key=private_key_seller,
            public_key=public_key_seller,
            policy_name=policy_b,
        )

        return buyer, seller, policy_c


def test_make_match_decision_with_policies(setup_agents_with_policies):
    """Test the make_match_decision method with different policies."""
    buyer, seller, policy_c = setup_agents_with_policies

    mock_message = {
        "pubkey": "0x123",
        "offerId": "offer_0",
        "initial": True,
        "data": {"_tag": "offer", "query": "hello", "price": ["0x100", 200]},
    }

    buyer.policy = Policy(public_key=public_key_buyer, policy_name=policy_c)
    buyer.negotiate_match = MagicMock()

    # TODO: make this scheme-compliant
    # TODO: more in general, test the scheme compliance of policies.
    def mock_infer(message):
        return "accept"

    buyer.policy.infer = MagicMock(side_effect=mock_infer)
    buyer.policy.infer(mock_message)


if __name__ == "__main__":
    pytest.main()
