"""This module defines message schemes to take part in various applications."""

from typing import Optional, Tuple, Union

from pydantic import BaseModel


class Offer(BaseModel):
    """Define the Offer model."""

    query: str
    price: Tuple[str, int]


class OfferMessage(BaseModel):
    """Offer Message."""

    _tag: str = "offer"
    query: str
    price: Tuple[str, int]


class CancelMessage(BaseModel):
    """Cancel Message."""

    _tag: str = "cancel"
    error: Optional[str] = None


class BuyAttestMessage(BaseModel):
    """Buy Attest Message."""

    _tag: str = "buyAttest"
    attestation: str
    offer: Offer


class SellAttestMessage(BaseModel):
    """Sell Attest Message."""

    _tag: str = "sellAttest"
    attestation: str
    result: str


Message = Union[OfferMessage, CancelMessage, BuyAttestMessage, SellAttestMessage]
