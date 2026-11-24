from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy import ARRAY
from sqlalchemy.dialects import postgresql
from sqlmodel import INTEGER, Column, Field, Relationship, SQLModel


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"  # type: ignore

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    content: str
    weight: float = Field(le=25)
    destination: int
    status: ShipmentStatus
    estimated_delivery: datetime

    seller_id: UUID = Field(foreign_key="seller.id")
    seller: "Seller" = Relationship(
        back_populates="shipments", sa_relationship_kwargs={"lazy": "selectin"}
    )

    delivery_partner_id: UUID = Field(foreign_key="delivery_partner.id")
    delivery_partner: "DeliveryPartner" = Relationship(
        back_populates="shipments", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Seller(SQLModel, table=True):
    __tablename__ = "seller"
    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    name: str
    address: int
    email: EmailStr
    pass_hash: str
    shipments: list[Shipment] = Relationship(back_populates="seller")
    created_at: datetime = Field(
        sa_column=Column(postgresql.TIME, default=datetime.now)
    )


class DeliveryPartner(SQLModel, table=True):
    __tablename__ = "delivery_partner"
    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )

    name: str
    address: int
    email: EmailStr
    pass_hash: str

    del_code: list[int] = Field(sa_column=Column(ARRAY(INTEGER)))

    max_handling_capacity: int
    shipments: list[Shipment] = Relationship(back_populates="delivery_partner")
    created_at: datetime = Field(
        sa_column=Column(postgresql.TIME, default=datetime.now)
    )
