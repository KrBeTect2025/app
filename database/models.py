"""
Database tables, defined as Python classes with SQLModel.

SQLModel = SQLAlchemy (the ORM that talks to the database) + Pydantic (data
validation). A class with `table=True` becomes a real table; each typed
attribute becomes a column.

Tables and how they connect:

    seller 1 ──< many shipment >── 1 delivery_partner

    - a seller creates many shipments          (shipment.seller_id)
    - a delivery partner delivers many of them (shipment.delivery_partner_id)

`Relationship(...)` fields are NOT columns. They let you write
`shipment.seller` or `partner.shipments` and get the related objects, which
SQLAlchemy loads using the foreign key columns.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy import ARRAY
from sqlalchemy.dialects import postgresql
from sqlmodel import INTEGER, Column, Field, Relationship, SQLModel


class ShipmentStatus(str, Enum):
    """Every state a shipment goes through, in order.

    Inheriting from `str` makes each value a plain string, so it's stored
    and returned in JSON as e.g. "in_transit".
    """

    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"


# Shared fields of every user type (seller, delivery partner); not a table itself
# (no `table=True`), so its columns are copied into each table that inherits it.
class User(SQLModel):
    name: str
    email: EmailStr
    # Only the bcrypt HASH of the password is stored, never the password itself
    pass_hash: str


class Shipment(SQLModel, table=True):
    """A package a seller sends, delivered by one delivery partner."""

    __tablename__ = "shipment"  # type: ignore

    # Primary key: a random UUID created by the app (uuid4) when inserting.
    # UUIDs can't be guessed like 1, 2, 3... ids, so ids don't leak counts.
    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    content: str
    weight: float = Field(le=25)  # le = "less than or equal": max 25 (kg)
    destination: int  # zip code it goes to; used to pick a delivery partner
    status: ShipmentStatus
    estimated_delivery: datetime

    # --- Who sent it ---
    # Column: the seller's id. foreign_key makes the DB reject unknown ids.
    seller_id: UUID = Field(foreign_key="seller.id")
    # Not a column: the Seller object itself, loaded via seller_id.
    # "Seller" is in quotes because the class is defined further down.
    # lazy="selectin" loads it together with the shipment (see DeliveryPartner).
    seller: "Seller" = Relationship(
        back_populates="shipments", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # --- Who delivers it ---
    delivery_partner_id: UUID = Field(foreign_key="delivery_partner.id")
    delivery_partner: "DeliveryPartner" = Relationship(
        back_populates="shipments", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Seller(User, table=True):
    """A business that creates shipments. Gets name, email, pass_hash from User."""

    __tablename__ = "seller"
    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    address: int  # the seller's zip code
    # All shipments this seller created. back_populates links it to
    # Shipment.seller, so setting one side updates the other.
    shipments: list[Shipment] = Relationship(back_populates="seller")
    # Filled in automatically when the row is inserted.
    # Note: postgresql.TIME stores only the time of day (no date).
    created_at: datetime = Field(
        sa_column=Column(postgresql.TIME, default=datetime.now)
    )


class DeliveryPartner(User, table=True):
    """A courier who delivers shipments to the zip codes in `del_code`."""

    __tablename__ = "delivery_partner"
    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )

    address: int

    # Zip codes this partner delivers to, stored as a PostgreSQL integer array
    # (one column holding a list, e.g. {110001,110002}).
    del_code: list[int] = Field(sa_column=Column(ARRAY(INTEGER)))

    # Most shipments the partner can handle at the same time
    max_handling_capacity: int
    # selectin: load shipments with the partner (lazy loading fails in async code)
    shipments: list[Shipment] = Relationship(
        back_populates="delivery_partner", sa_relationship_kwargs={"lazy": "selectin"}
    )
    created_at: datetime = Field(
        sa_column=Column(postgresql.TIME, default=datetime.now)
    )

    # Shipments the partner is still handling (not delivered yet)
    # @property: used like an attribute (partner.active_shipments), computed
    # in Python each time; it is not stored in the database.
    @property
    def active_shipments(self) -> list[Shipment]:
        return [
            shipment
            for shipment in self.shipments
            if shipment.status != ShipmentStatus.delivered
        ]

    # How many more shipments the partner can take right now
    @property
    def current_handling_capacity(self) -> int:
        return self.max_handling_capacity - len(self.active_shipments)
