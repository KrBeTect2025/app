from datetime import datetime, timedelta, timezone  # noqa: EXE002

import jwt
from fastapi import HTTPException, status

from config import security_settings

from uuid import uuid4


def generate_access_token(data: dict, exp: timedelta = timedelta(days=1)) -> str:
    return jwt.encode(
        payload={
            **data,
            "jti": str(
                uuid4()
            ),  # wrapped inside the the type cast of th str beacsue the uui4 return UUID object and we need json compatablity
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

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="expired")
    except jwt.PyJWTError as e:
        print(f"{e} : token isnt valid")
        return None
