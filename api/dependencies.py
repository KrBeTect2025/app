"""
Dependencies that FastAPI prepares before a route runs.

Read top to bottom, in the order FastAPI builds them:

    1. Database session  -> one per request, shared by everything below
    2. Services          -> the classes that do the database work
    3. Authentication    -> token from header -> token is valid -> load the user

Routes just ask for what they need, e.g.

    async def submit_shipment(..., service: ServiceDep, seller: SellerDep): ...
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import oauth2_scheme_partner, oauth2_scheme_seller
from database.models import DeliveryPartner, Seller
from database.redis import is_jti_blacklisted
from database.session import get_session
from services.delivery_partner import DeliveryPartnerService
from services.seller import SellerService
from services.shipment import ShipmentService
from services.util import decode_access_token

# ---------------------------------------------------------------------------
# 1. Database session
# ---------------------------------------------------------------------------

SessionDep = Annotated[AsyncSession, Depends(get_session)]


# ---------------------------------------------------------------------------
# 2. Services
# ---------------------------------------------------------------------------


def get_seller_service(session: SessionDep) -> SellerService:
    return SellerService(session)


SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]


def get_delivery_partner_service(session: SessionDep) -> DeliveryPartnerService:
    return DeliveryPartnerService(session)


DeliveryPartnerServiceDep = Annotated[
    DeliveryPartnerService, Depends(get_delivery_partner_service)
]


def get_shipment_service(
    session: SessionDep,
    partner_service: DeliveryPartnerServiceDep,
) -> ShipmentService:
    # Needs the partner service to assign each new shipment to a partner
    return ShipmentService(session, partner_service)


ServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]


# ---------------------------------------------------------------------------
# 3. Authentication
# ---------------------------------------------------------------------------


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


async def _validate_token(token: str) -> dict:
    """Decode the token; reject it if invalid or logged out (jti blacklisted)."""
    data = decode_access_token(token)

    if data is None or "jti" not in data:
        raise _unauthorized("Invalid access token")
    if await is_jti_blacklisted(data["jti"]):
        raise _unauthorized("Invalid access token")

    return data


# --- Token data (also used directly by the logout routes) ------------------


async def get_seller_access_token(
    token: Annotated[str, Depends(oauth2_scheme_seller)],
) -> dict:
    return await _validate_token(token)


async def get_partner_access_token(
    token: Annotated[str, Depends(oauth2_scheme_partner)],
) -> dict:
    return await _validate_token(token)


# --- Logged-in user --------------------------------------------------------


async def get_current_seller(
    token_data: Annotated[dict, Depends(get_seller_access_token)],
    session: SessionDep,
) -> Seller:
    seller = await session.get(Seller, UUID(token_data["user"]["id"]))
    if seller is None:
        raise _unauthorized("Not authorized")
    return seller


async def get_current_partner(
    token_data: Annotated[dict, Depends(get_partner_access_token)],
    session: SessionDep,
) -> DeliveryPartner:
    partner = await session.get(DeliveryPartner, UUID(token_data["user"]["id"]))
    if partner is None:
        raise _unauthorized("Not authorized")
    return partner


SellerDep = Annotated[Seller, Depends(get_current_seller)]
DeliveryPartnerDep = Annotated[DeliveryPartner, Depends(get_current_partner)]
