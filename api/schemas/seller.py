from pydantic import BaseModel, EmailStr, Field


class BaseSeller(BaseModel):
    name: str
    email: EmailStr


class SellerCreate(BaseSeller):
    # bcrypt only uses the first 72 bytes
    password: str = Field(min_length=8, max_length=72)


class SellerRead(BaseSeller):
    id: int
