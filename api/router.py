"""
Collects the routers of every feature into one master_router,
which main.py adds to the app with a single include_router call.

Each feature router sets its own URL prefix and docs tag:
    shipment.router         -> /shipment/...
    seller.router           -> /seller/...
    delivery_partner.router -> /partner/...
"""

from fastapi import APIRouter

from api.routers import delivery_partner, seller, shipment

master_router = APIRouter()
master_router.include_router(shipment.router)
master_router.include_router(seller.router)
master_router.include_router(delivery_partner.router)
