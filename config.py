"""
App settings, read from environment variables or the `.env` file.

pydantic-settings fills each class attribute from the environment variable
with the same name, converts it to the declared type (e.g. "5432" -> 5432),
and raises an error at startup if a required one is missing. So a typo in
.env fails loudly at launch, not later in the middle of a request.

Example `.env` (next to this file, never committed to git):

    POSTGRES_SERVER=localhost
    POSTGRES_PORT=5432
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=...
    POSTGRES_DB=fastapi_app
    REDIS_HOST=localhost
    REDIS_PORT=6379
    JWT_SECRET=...           (a long random string)
    JWT_ALGORITHM=HS256
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Connection details for PostgreSQL (main database) and Redis (cache)."""

    # --- PostgreSQL ---
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # --- Redis (rate limiting + logged-out token blacklist) ---
    REDIS_HOST: str
    REDIS_PORT: str

    model_config = SettingsConfigDict(
        # Look for .env in the same folder as this file, wherever you run from
        env_file=Path(__file__).parent / ".env",
        # Treat `KEY=` (empty value) as "not set"
        env_ignore_empty=True,
        # Other keys in .env (e.g. JWT_SECRET) are fine, just not used here
        extra="ignore",
    )

    @property
    def POSTGRES_URL(self):
        """Full database URL built from the parts above.

        Format: dialect+driver://user:password@host:port/database
        `asyncpg` is the async PostgreSQL driver, needed for async SQLAlchemy.
        """
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


class SecuritySettings(BaseSettings):
    """Settings for signing and checking JWT access tokens."""

    # Secret key that signs tokens. Anyone who has it can forge tokens.
    JWT_SECRET: str
    # Signing algorithm, e.g. HS256
    JWT_ALGORITHM: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # Values are loaded from .env at runtime, which type checkers can't see


# Created once when this module is first imported; everyone else imports
# these objects (`from config import db_settings`) instead of reading .env.
# The `type: ignore` is because the type checker thinks the required fields
# are missing; they come from .env at runtime.
security_settings = SecuritySettings()  # type: ignore[call-arg]
db_settings = DatabaseSettings()  # type: ignore
