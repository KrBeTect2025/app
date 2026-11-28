"""
Delivery partner routes: sign up, log in, update own profile, log out.

Works like api/routers/seller.py; see the comments there for signup,
token and logout.
"""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies import (
    DeliveryPartnerDep,
    DeliveryPartnerServiceDep,
    get_partner_access_token,
)
from api.schemas.delivery_partner import (
    DeliveryPartnerCreate,
    DeliveryPartnerRead,
    DeliveryPartnerUpdate,
)
from database.redis import add_jti_to_blacklist

router = APIRouter(prefix="/partner", tags=["Delivery Partner"])


### Register a new delivery partner
@router.post("/signup", response_model=DeliveryPartnerRead)
async def register_delivery_partner(
    delivery_partner: DeliveryPartnerCreate, service: DeliveryPartnerServiceDep
):
    return await service.add(delivery_partner)


### Log in: email (as `username`) + password -> access token
@router.post("/token")
async def login_delivery_partner(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: DeliveryPartnerServiceDep,
):
    token = await service.token(request_form.username, request_form.password)
    return {
        "access_token": token,
        "token_type": "bearer",
    }


### Update the logged in delivery partner
# DeliveryPartnerDep = the partner from the token, so a partner can only
# ever change their own profile; there is no id in the URL to tamper with.
@router.patch("/", response_model=DeliveryPartnerRead)
async def update_delivery_partner(
    partner_update: DeliveryPartnerUpdate,
    partner: DeliveryPartnerDep,
    service: DeliveryPartnerServiceDep,
):
    # Update data with given fields (drop the ones the client didn't send)
    update = partner_update.model_dump(exclude_none=True)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )

    # Copy the new values onto the partner object, then save it
    partner.sqlmodel_update(update)
    return await service.update(partner)


### Log out: block the current token until it expires
@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_delivery_partner(
    token_data: Annotated[dict, Depends(get_partner_access_token)],
):
    seconds_left = int(token_data["exp"] - datetime.now(UTC).timestamp())
    await add_jti_to_blacklist(token_data["jti"], max(seconds_left, 1))
