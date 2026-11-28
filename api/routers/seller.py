"""
Seller routes: sign up, log in, log out.

Routes stay thin: they receive validated input (FastAPI + the schemas),
call a service method, and return the result. The work is in
services/seller.py.
"""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies import SellerServiceDep, get_seller_access_token
from api.schemas.seller import SellerCreate, SellerRead
from database.redis import add_jti_to_blacklist

# prefix: every route below starts with /seller
# tags: groups these routes under "Seller" in the /docs page
router = APIRouter(prefix="/seller", tags=["Seller"])


### Register a new seller
# response_model=SellerRead: the response is filtered through SellerRead,
# so fields like pass_hash are never sent back, even though the Seller
# object returned by the service has them.
@router.post("/signup", response_model=SellerRead)
async def register_seller(seller: SellerCreate, service: SellerServiceDep):
    return await service.add(seller)


### Log in: email + password -> access token
# OAuth2PasswordRequestForm reads a FORM body (not JSON) with the fields
# `username` and `password`; that's what the OAuth2 standard and the
# "Authorize" button on /docs send. Here the username is the email.
@router.post("/token")
async def login_seller(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: SellerServiceDep,
):
    token = await service.token(request_form.username, request_form.password)
    # This exact shape is what OAuth2 clients (like /docs) expect back
    return {
        "access_token": token,
        "token_type": "bearer",
    }


### Log out: block the current token until it would have expired anyway
# 204 No Content: success, with an empty response body.
@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_seller(token_data: Annotated[dict, Depends(get_seller_access_token)]):
    # "exp" in the token is a Unix timestamp (seconds since 1970)
    seconds_left = int(token_data["exp"] - datetime.now(timezone.utc).timestamp())
    # At least 1 second, because Redis rejects an expiry of 0 or less
    await add_jti_to_blacklist(token_data["jti"], max(seconds_left, 1))
