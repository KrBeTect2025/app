from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.seller import SellerCreate
from config import security_settings
from database.models import Seller

password_context = CryptContext(schemes="bcrypt")


class SellerService:
    def __init__(self, session: AsyncSession):
        # Get database session to perform database operations
        self.session = session

    # Add a new seller with hashed password
    async def add(self, credentials: SellerCreate) -> Seller:
        seller = Seller(
            **credentials.model_dump(exclude={"password"}),  # type: ignore[arg-type]
            # hashed password
            pass_hash=password_context.hash(credentials.password)
        )
        self.session.add(seller)
        await self.session.commit()
        await self.session.refresh(seller)

        return seller

    async def token(self, email, password) -> str:
        # validate the cred
        result = await self.session.execute(select(Seller).where(Seller.email == email))
        seller = result.scalar()

        if seller is None or not password_context.verify(password, seller.pass_hash):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="email or password are wrongd",
            )

        token = jwt.encode(
            payload={
                "user": {"name": seller.name, "email": seller.email},
                "exp": datetime.now(timezone.utc) + timedelta(days=1),
            },
            algorithm=security_settings.JWT_ALGORITHM,
            key=security_settings.JWT_SECRET,
        )
        return token
