"""Has Oauth2passworf bearere"""

from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer , HTTPBearer

from services.util import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/seller/token")


class AccessTokenBearer(HTTPBearer):
    async def __call__(self, request):
        request.header.get("Authorization").split(" ")[1]
        auth_credentials = await super().__call__(request)
        token = auth_credentials.credentials

        token_data = decode_access_token(token)

        if token_data is None:
            raise HTTPException(status_code=401 , detail="Not Autharize"
                                )

        return token_data

access_token_bearer = AccessTokenBearer()

Annotated[dict , Depends(access_token_bearer)]



