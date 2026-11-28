"""
Schemas: the shape of JSON going IN to and OUT of the /partner routes.
Same Base / Create / Read pattern as api/schemas/seller.py, plus Update.
"""

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class BaseDeliveryPartner(BaseModel):
    name: str
    email: EmailStr
    address: int
    # zip codes the partner delivers to (stored in the `del_code` column)
    del_code: list[int]
    # most shipments the partner can handle at once
    max_handling_capacity: int


class DeliveryPartnerCreate(BaseDeliveryPartner):
    """Request body of POST /partner/signup."""

    # bcrypt only uses the first 72 bytes
    password: str = Field(min_length=8, max_length=72)


class DeliveryPartnerRead(BaseDeliveryPartner):
    """What the API returns for a partner (no password)."""

    id: UUID


class DeliveryPartnerUpdate(BaseModel):
    """Request body of PATCH /partner/.

    Every field is optional (default None), so the client sends only what
    changes. The route drops the None fields before saving.
    """

    del_code: list[int] | None = Field(default=None)
    max_handling_capacity: int | None = Field(default=None)
