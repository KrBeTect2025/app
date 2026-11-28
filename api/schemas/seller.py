"""
Schemas: the shape of JSON going IN to and OUT of the seller routes.

Schemas are separate from the database models on purpose:
- the client never sends an `id` (the DB creates it),
- the API never sends back the password or its hash.

Pattern used in every schema file:
    Base...    fields shared by input and output
    ...Create  what the client sends to create one (Base + password)
    ...Read    what the API returns (Base + id)
"""

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class BaseSeller(BaseModel):
    name: str
    email: EmailStr  # Pydantic checks it looks like a real email address
    address: int  # zip code


class SellerCreate(BaseSeller):
    """Request body of POST /seller/signup."""

    # bcrypt only uses the first 72 bytes
    password: str = Field(min_length=8, max_length=72)


class SellerRead(BaseSeller):
    """What the API returns for a seller (no password)."""

    id: UUID
