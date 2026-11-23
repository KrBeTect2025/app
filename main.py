from contextlib import asynccontextmanager

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from api.middleware import rate_limiter
from api.router import master_router
from database.redis import close_redis
from database.session import create_db_tables


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    yield
    await close_redis()


app = FastAPI(
    # Server start/stop listener
    lifespan=lifespan_handler,
)
app.middleware("http")(rate_limiter)
app.include_router(master_router)


### Scalar API Documentation
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )
