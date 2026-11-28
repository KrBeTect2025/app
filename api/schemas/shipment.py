"""
Schemas: the shape of JSON going IN to and OUT of the /shipment routes.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from database.models import ShipmentStatus


class BaseShipment(BaseModel):
    content: str
    weight: float = Field(le=25)  # max 25 (kg); more gets a 422 error
    destination: int  # zip code


class ShipmentRead(BaseShipment):
    """What the API returns for a shipment."""

    id: UUID
    status: ShipmentStatus
    estimated_delivery: datetime


class ShipmentCreate(BaseShipment):
    """Request body of POST /shipment/.

    Same as BaseShipment: status, ETA, seller and partner are set by the
    server, not by the client (see ShipmentService.add).
    """

    pass


class ShipmentUpdate(BaseModel):
    """Request body of PATCH /shipment/. Send only the fields that change."""

    status: ShipmentStatus | None = Field(default=None)
    estimated_delivery: datetime | None = Field(default=None)
