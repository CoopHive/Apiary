from unittest.mock import MagicMock

import pytest

from coophive.deal import Deal
from coophive.match import Match
from coophive.result import Result
from coophive.smart_contract import SmartContract
from coophive.utils import Tx


@pytest.fixture
def smart_contract():
    """Fixture for the SmartContract instance."""
    return SmartContract("public_key")


@pytest.fixture
def tx():
    """Fixture for a transaction."""
    return Tx("sender", 100)


def test_initial_balance(smart_contract):
    """Test that the initial balance of the smart contract is zero."""
    assert smart_contract.balance == 0


def test_agree_to_match_seller(smart_contract, tx):
    """Test seller agreement to a match."""
    match = Match()
    match.set_attributes({"timeout_deposit": 100, "seller_address": "provider_address"})

    tx.value = 100
    tx.sender = "provider_address"
    smart_contract.balances["provider_address"] = 150

    smart_contract._agree_to_match_seller(match, tx)
    assert smart_contract.balances["provider_address"] == 50
    assert smart_contract.balance == 100
    assert match.seller_signed


def test_agree_to_match_buyer(smart_contract, tx):
    """Test buyer agreement to a match."""
    match = Match()
    match.set_attributes({"buyer_deposit": 100, "buyer_address": "buyer_address"})
    tx.value = 100
    tx.sender = "buyer_address"
    smart_contract.balances["buyer_address"] = 150
    match.sign_buyer = MagicMock()

    smart_contract._agree_to_match_buyer(match, tx)
    assert smart_contract.balances["buyer_address"] == 50
    assert smart_contract.balance == 100
    match.sign_buyer.assert_called_once()


def test_agree_to_match(smart_contract, tx):
    """Test both seller and buyer agreements to a match."""
    match = Match()
    match.set_attributes(
        {
            "timeout_deposit": 100,
            "seller_address": "provider_address",
            "buyer_deposit": 100,
            "buyer_address": "buyer_address",
        }
    )
    tx.value = 100
    tx.sender = "provider_address"
    smart_contract.balances["provider_address"] = 150
    smart_contract.balances["buyer_address"] = 150

    smart_contract.agree_to_match(match, tx)
    assert smart_contract.balances["provider_address"] == 50
    assert smart_contract.balance == 100

    tx.sender = "buyer_address"
    smart_contract.agree_to_match(match, tx)
    assert smart_contract.balances["buyer_address"] == 50
    assert smart_contract.balance == 200
    assert match in smart_contract.matches_made_in_current_step


def test_create_deal(smart_contract):
    """Test the creation of a deal."""
    match = Match()
    match.set_attributes(
        {
            "seller_address": "provider_address",
            "buyer_address": "buyer_address",
        }
    )
    smart_contract._create_deal(match)
    assert len(smart_contract.deals) == 1


def test_post_result(smart_contract, tx):
    """Test posting a result."""
    result = Result()
    smart_contract.post_result(result, tx)
    assert [result, tx] in smart_contract.results_posted_in_current_step


def test_refund_buyer_deposit(smart_contract):
    """Test refunding the buyer's deposit."""
    deal = Deal()
    deal.set_attributes({"buyer_address": "buyer_address", "buyer_deposit": 100})
    smart_contract.balances["buyer_address"] = 0
    smart_contract._refund_buyer_deposit(deal)
    assert smart_contract.balances["buyer_address"] == 100
    assert smart_contract.balance == -100


if __name__ == "__main__":
    pytest.main()
