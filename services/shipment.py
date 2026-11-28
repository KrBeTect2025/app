"""
ShipmentService: create, read, update and delete shipments.

Creating one also picks a delivery partner, so this service gets a
DeliveryPartnerService handed in (see get_shipment_service in
api/dependencies.py). Passing it in, instead of creating it here, is
"dependency injection": both services share the same request session.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.shipment import ShipmentCreate
from database.models import Seller, Shipment, ShipmentStatus

from .base import BaseService
from .delivery_partner import DeliveryPartnerService


class ShipmentService(BaseService):
    def __init__(self, session: AsyncSession, partner_service: DeliveryPartnerService):
        super().__init__(Shipment, session)
        self.partner_service = partner_service

    # Get a shipment by id
    async def get(self, id: UUID) -> Shipment | None:
        return await self._get(id)

    # Add a new shipment and assign a delivery partner to it
    async def add(self, shipment_create: ShipmentCreate, seller: Seller) -> Shipment:
        new_shipment = Shipment(
            # content, weight, destination from the request body
            **shipment_create.model_dump(),
            # the rest is decided by the server:
            status=ShipmentStatus.placed,
            # now + 3 days. tzinfo=None because the DB column has no timezone
            estimated_delivery=datetime.now(timezone.utc).replace(tzinfo=None)
            + timedelta(days=3),
            seller_id=seller.id,
        )
        # Raises 406 if no partner can take it
        partner = await self.partner_service.assign_shipment(new_shipment)
        new_shipment.delivery_partner_id = partner.id

        return await self._add(new_shipment)

    # Get a shipment by id or raise 404
    async def get_or_404(self, id: UUID) -> Shipment:
        shipment = await self.get(id)
        if shipment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Given id doesn't exist!",
            )
        return shipment

    # Update an existing shipment
    async def update(self, id: UUID, shipment_update: dict) -> Shipment:
        shipment = await self.get_or_404(id)
        # copy the given fields (e.g. {"status": "in_transit"}) onto the object
        shipment.sqlmodel_update(shipment_update)
        return await self._update(shipment)

    # Delete a shipment
    async def delete(self, id: UUID) -> None:
        await self._delete(await self.get_or_404(id))
