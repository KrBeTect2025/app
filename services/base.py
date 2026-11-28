"""
BaseService: the four basic database operations (get, add, update, delete),
written once and reused by every service through inheritance.

    BaseService
     ├── ShipmentService
     └── UserService                (adds password hashing + login)
          └── DeliveryPartnerService

The methods start with `_` ("for subclasses, not for routes"). Each service
exposes its own public methods (get, add, ...) with the exact types it needs.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel


class BaseService:
    def __init__(self, model: type[SQLModel], session: AsyncSession):
        # Model (table) this service works with, e.g. Shipment
        self.model = model
        # Get database session to perform database operations
        self.session = session

    # Get an entity by its primary key (None if there is no such row)
    async def _get(self, id: UUID):
        return await self.session.get(self.model, id)

    # Add a new entity to the database
    async def _add(self, entity: SQLModel):
        self.session.add(entity)  # stage the INSERT (nothing sent yet)
        await self.session.commit()  # send it to the database and save
        await self.session.refresh(entity)  # reload DB-made values (id, defaults)
        return entity

    # Save changes made to an existing entity
    # (session.add on an existing object just marks it for UPDATE instead)
    async def _update(self, entity: SQLModel):
        return await self._add(entity)

    # Remove an entity from the database
    async def _delete(self, entity: SQLModel) -> None:
        await self.session.delete(entity)
        await self.session.commit()
