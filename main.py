"""
Entry point of the app: creates the FastAPI application and wires it together.

Run it with:

    fastapi dev main.py          (or: uvicorn main:app --reload)

What happens to a request, from the outside in:

    request
      -> rate_limiter middleware   (api/middleware.py)   too many? -> 429
      -> master_router             (api/router.py)       which URL? -> which route
      -> dependencies              (api/dependencies.py) session, service, logged-in user
      -> route function            (api/routers/*.py)    validates input, calls a service
      -> service                   (services/*.py)       the real work, talks to the DB
    response
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from api.middleware import rate_limiter
from api.router import master_router
from database.redis import close_redis
from database.session import create_db_tables


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    """Code that runs once when the server starts, and once when it stops.

    Everything before `yield` runs at startup, everything after it at shutdown.
    """
    # Startup: make sure every table from database/models.py exists
    await create_db_tables()

    yield  # <- the server is running and handling requests here

    # Shutdown: close the Redis connection cleanly
    await close_redis()


app = FastAPI(
    # Server start/stop listener (see lifespan_handler above)
    lifespan=lifespan_handler,
)

# Run rate_limiter on EVERY http request, before it reaches any route.
# Same as decorating rate_limiter with @app.middleware("http").
app.middleware("http")(rate_limiter)

# Add all routes (/seller/..., /partner/..., /shipment/...) to the app
app.include_router(master_router)


### Scalar API Documentation
# An alternative to the built-in /docs page. Open http://localhost:8000/scalar
# include_in_schema=False hides this route itself from the API docs.
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        # The OpenAPI JSON that FastAPI generates from all routes (/openapi.json)
        openapi_url=app.openapi_url,
        title="Scalar API",
    )
