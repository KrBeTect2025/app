"""
Security schemes: how the API finds the access token in a request.

OAuth2PasswordBearer reads the header

    Authorization: Bearer <token>

and returns just the <token> string (or answers 401 if the header is
missing). `tokenUrl` tells the /docs page which route issues tokens, so its
"Authorize" button can log you in. There are two because sellers and
delivery partners log in at different URLs.

Checking that the token is valid happens later, in api/dependencies.py.
"""

from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer , HTTPBearer

from services.util import decode_access_token

oauth2_scheme_seller = OAuth2PasswordBearer(tokenUrl="/seller/token", scheme_name="Seller")
oauth2_scheme_partner = OAuth2PasswordBearer(tokenUrl="/partner/token", scheme_name="DeliveryPartner")


# ---------------------------------------------------------------------------
# NOT USED anywhere yet: an earlier experiment with a different approach.
# HTTPBearer also reads "Authorization: Bearer <token>", but without the
# login form on /docs. As written it would crash if used:
#   - `request.header` should be `request.headers`, and the result of that
#     line is thrown away anyway (super().__call__ already extracts it).
# ---------------------------------------------------------------------------
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

# This line does nothing: it builds a type and doesn't store it. To use it,
# it would need a name, e.g. `AccessTokenDep = Annotated[...]`.
Annotated[dict , Depends(access_token_bearer)]
