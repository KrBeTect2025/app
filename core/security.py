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

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme_seller = OAuth2PasswordBearer(
    tokenUrl="/seller/token", scheme_name="Seller"
)
oauth2_scheme_partner = OAuth2PasswordBearer(
    tokenUrl="/partner/token", scheme_name="DeliveryPartner"
)
