from datetime import datetime, timedelta, timezone

import jwt

from config import security_settings


def generate_access_token(data: dict, exp: timedelta = timedelta(days=1)) -> str:
    return jwt.encode(
        payload={
            **data,
            "exp": datetime.now(timezone.utc) + exp,
        },
        algorithm=security_settings.JWT_ALGORITHM,
        key=security_settings.JWT_SECRET,
    )


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            jwt=token,
            key=security_settings.JWT_SECRET,
            algorithms=[security_settings.JWT_ALGORITHM],
        )

    except jwt.PyJWTError as e:
        print(f"{e} : token isnt valid")
        return None
