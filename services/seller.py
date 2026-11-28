"""
SellerService: sign up and log in for sellers.

Note: this is the older version of the logic in services/user.py, written
before UserService existed. It does the same thing; DeliveryPartnerService
shows the shorter way (inherit from UserService).
"""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.seller import SellerCreate
from config import security_settings
from database.models import Seller
from services.util import generate_access_token

# bcrypt password hasher (same as in services/user.py)
password_context = CryptContext(schemes="bcrypt")


class SellerService:
    def __init__(self, session: AsyncSession):
        # Get database session to perform database operations
        self.session = session

    # Add a new seller with hashed password
    async def add(self, credentials: SellerCreate) -> Seller:
        seller = Seller(
            # every field except the password (name, email, address)
            **credentials.model_dump(exclude={"password"}),  # type: ignore[arg-type]
            # hashed password
            pass_hash=password_context.hash(credentials.password),
        )
        self.session.add(seller)
        await self.session.commit()
        await self.session.refresh(seller)  # load the new id from the DB

        return seller

    # Check email + password and return an access token (JWT)
    async def token(self, email, password):
        # validate the cred: find the seller with this email
        result = await self.session.execute(select(Seller).where(Seller.email == email))
        seller = result.scalar()  # first row, or None

        # Same error for unknown email and wrong password (don't leak which)
        if seller is None or not password_context.verify(password, seller.pass_hash):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="email or password are wrongd",
            )

        token = generate_access_token(
            data={"user": {"name": seller.name, "id": str(seller.id)}}
        )
        return token
