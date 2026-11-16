from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies import SellerServiceDep, SessionDep, get_access_token
from api.schemas.seller import SellerCreate, SellerRead
from core.security import oauth2_scheme
from database.models import Seller
from database.redis import add_jti_to_blacklist
from services.util import decode_access_token

router = APIRouter(prefix="/seller", tags=["Seller"])


### Register a new seller
@router.post("/signup", response_model=SellerRead)
async def register_seller(seller: SellerCreate, service: SellerServiceDep):
    return await service.add(seller)


@router.post("/token")
async def login_seller(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: SellerServiceDep,
):
    token = await service.token(request_form.username, request_form.password)
    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_seller(token_data: Annotated[dict, Depends(get_access_token)]):
    seconds_left = int(token_data["exp"] - datetime.now(timezone.utc).timestamp())
    await add_jti_to_blacklist(token_data["jti"], max(seconds_left, 1))
