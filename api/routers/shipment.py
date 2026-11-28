"""
Shipment routes: create, read, update and delete shipments.

Who may do what is decided by the dependencies each route asks for:
    SellerDep          -> needs a valid SELLER token (sent by a seller)
    DeliveryPartnerDep -> needs a valid PARTNER token
Asking for one is enough: if the token is missing or wrong, FastAPI
answers 401 before the route body runs.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

# `..` = the parent package (api/), same as `from api.dependencies import ...`
from ..dependencies import DeliveryPartnerDep, SellerDep, ServiceDep
from ..schemas.shipment import ShipmentCreate, ShipmentRead, ShipmentUpdate

# api router to group endpoints
router = APIRouter(prefix="/shipment", tags=["Shipment"])


### Read a shipment by id
# `id` isn't in the path, so FastAPI reads it from the query string:
# GET /shipment/?id=<uuid>   (and returns 422 if it isn't a valid UUID)
@router.get("/", response_model=ShipmentRead)
async def get_shipment(id: UUID, service: ServiceDep , seller : SellerDep):
    # Check for shipment with given id
    shipment = await service.get(id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given id doesn't exist!",
        )

    return shipment


### Create a new shipment with content and weight
# The logged-in seller becomes the shipment's seller, and the service
# picks a delivery partner for the destination zip code.
@router.post("/", response_model=ShipmentRead)
async def submit_shipment(
    shipment: ShipmentCreate, service: ServiceDep, seller: SellerDep
):
    return await service.add(shipment, seller)


### Update the status / ETA of a shipment (delivery partners only)
# `partner` isn't used in the body; asking for it is what enforces
# "only a logged-in delivery partner may call this".
@router.patch("/", response_model=ShipmentRead)
async def update_shipment(
    id: UUID,
    shipment_update: ShipmentUpdate,
    service: ServiceDep,
    partner: DeliveryPartnerDep,
):
    # Update data with given fields (drop the ones the client didn't send)
    update = shipment_update.model_dump(exclude_none=True)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )

    return await service.update(id, update)


### Delete a shipment by id
# Note: asks for no SellerDep / DeliveryPartnerDep, so anyone can call it.
@router.delete("/")
async def delete_shipment(id: UUID, service: ServiceDep) -> dict[str, str]:
    # Remove from database (404 if the id doesn't exist)
    await service.delete(id)

    return {"detail": f"Shipment with id #{id} is deleted!"}
