"""
Connection to PostgreSQL: the engine (connection pool) and per-request sessions.

- engine:  created ONCE for the whole app; keeps a pool of open connections.
- session: created PER REQUEST (get_session); a "unit of work" where you add,
           change and delete objects, then `commit()` to save them all at once.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from config import db_settings

# Create a database engine to connect with database
engine = create_async_engine(
    # database type/dialect, driver, login and database name (see config.py)
    url=db_settings.POSTGRES_URL,
    # Log every SQL query to the terminal: great for learning what the ORM does
    echo=True,
)


async def create_db_tables():
    """Create every table defined in database/models.py that doesn't exist yet.

    Called once at startup (see main.py). It never changes existing tables;
    schema changes go through Alembic migrations (the migrations/ folder).
    """
    async with engine.begin() as connection:
        # Importing the models registers their tables in SQLModel.metadata.
        # Without this import, metadata might be empty and nothing is created.
        from database.models import Shipment  # noqa: F401

        # create_all is synchronous code; run_sync runs it on the async connection
        await connection.run_sync(SQLModel.metadata.create_all)


async def get_session():
    """Dependency: give one database session to a request, then close it.

    Because this is a generator (`yield`), FastAPI runs the code before yield
    before the route, hands the session to the route, and finishes the
    `async with` block (closing the session) after the response is sent.
    """
    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        # Keep objects usable after commit(). Otherwise reading e.g.
        # `seller.id` after commit would need a new query, which in async
        # code raises an error instead of quietly running it.
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
