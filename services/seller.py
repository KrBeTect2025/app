from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.seller import SellerCreate
from database.models import Seller

password_context = CryptContext(schemes="bcrypt")


class SellerService:
    def __init__(self, session: AsyncSession):
        # Get database session to perform database operations
        self.session = session

    # Add a new seller with hashed password
    async def add(self, credentials: SellerCreate):
        seller = Seller(
            **credentials.model_dump(exclude={"password"}),  # type: ignore[arg-type]
            # hashed password
            pass_hash=password_context.hash(credentials.password)
        )
        self.session.add(seller)
