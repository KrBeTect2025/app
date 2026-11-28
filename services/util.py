"""
JWT helpers: create and read access tokens.

A JWT (JSON Web Token) is three base64 parts joined by dots:

    header.payload.signature

The payload is readable by anyone (it's NOT encrypted), but the signature
is made with JWT_SECRET. If anyone changes the payload, the signature no
longer matches and decoding fails. So the server can trust what it reads
without storing tokens anywhere.
"""

from datetime import datetime, timedelta, timezone  # noqa: EXE002
from uuid import uuid4

import jwt
from fastapi import HTTPException, status

from config import security_settings


def generate_access_token(data: dict, exp: timedelta = timedelta(days=1)) -> str:
    """Sign `data` into a token that is valid for `exp` (default: 1 day)."""
    return jwt.encode(
        payload={
            **data,
            # jti = "JWT id": a unique id per token, so one token can be
            # logged out (blacklisted) without affecting others.
            # str(): uuid4() returns a UUID object, and JSON needs a string.
            "jti": str(uuid4()),
            # exp = expiry time; jwt.decode rejects the token after this
            "exp": datetime.now(timezone.utc) + exp,
        },
        algorithm=security_settings.JWT_ALGORITHM,
        key=security_settings.JWT_SECRET,
    )


def decode_access_token(token: str) -> dict | None:
    """Check the token's signature and expiry, and return its payload.

    - expired token        -> raises 401 "expired"
    - any other bad token  -> returns None (the caller raises the 401)
    """
    try:
        return jwt.decode(
            jwt=token,
            key=security_settings.JWT_SECRET,
            # A list of accepted algorithms. Fixing it here stops an attacker
            # from sending a token that claims a weaker algorithm.
            algorithms=[security_settings.JWT_ALGORITHM],
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="expired")
    except jwt.PyJWTError as e:
        print(f"{e} : token isnt valid")
        return None
