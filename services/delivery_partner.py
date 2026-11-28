"""
DeliveryPartnerService: partner accounts, and choosing a partner for a
new shipment.

Sign up / log in come from UserService; this class just adds the
partner-specific parts.
"""

from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import any_, select

from api.schemas.delivery_partner import DeliveryPartnerCreate
from database.models import DeliveryPartner, Shipment

from .user import UserService


class DeliveryPartnerService(UserService):
    def __init__(self, session: AsyncSession):
        # Tell the base classes which table this service works with
        super().__init__(DeliveryPartner, session)

    # Add a new delivery partner with hashed password
    async def add(self, delivery_partner: DeliveryPartnerCreate) -> DeliveryPartner:
        return await self._add_user(delivery_partner.model_dump())

    # Validate the credentials and return an access token
    async def token(self, email: str, password: str) -> str:
        return await self._generate_token(email, password)

    # Save changes made to a delivery partner
    async def update(self, partner: DeliveryPartner) -> DeliveryPartner:
        return await self._update(partner)

    # Delivery partners that deliver to the given zip code
    async def get_partners_by_zipcode(self, zipcode: int) -> Sequence[DeliveryPartner]:
        # `in` doesn't work on a column; `value == any_(array_column)` does
        # SQL: SELECT * FROM delivery_partner WHERE :zipcode = ANY(del_code)
        return (
            await self.session.scalars(
                select(DeliveryPartner).where(
                    zipcode == any_(DeliveryPartner.del_code)
                )
            )
        ).all()

    # Assign the shipment to the first eligible partner with free capacity
    async def assign_shipment(self, shipment: Shipment) -> DeliveryPartner:
        eligible_partners = await self.get_partners_by_zipcode(shipment.destination)

        for partner in eligible_partners:
            if partner.current_handling_capacity > 0:
                # back_populates also sets shipment.delivery_partner(_id)
                partner.shipments.append(shipment)
                return partner

        # No partner serves this zip code, or all of them are at full capacity
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="No delivery partner available",
        )
