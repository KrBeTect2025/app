from pydantic import BaseModel, EmailStr


class SellerCreae(BaseModel):
    name: str
    email: EmailStr
    password: str
