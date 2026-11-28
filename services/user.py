"""
UserService: what every kind of user account needs (sign up, log in).

Shared by user types through inheritance, so the password logic lives in
one place. DeliveryPartnerService uses it; see services/seller.py for the
seller version.
"""

from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User

from .base import BaseService
from .util import generate_access_token

# Hashes and checks passwords with bcrypt. A hash is one-way: you can check
# a password against it, but you can't get the password back from it.
password_context = CryptContext(schemes="bcrypt")


class UserService(BaseService):
    def __init__(self, model: type[User], session: AsyncSession):
        super().__init__(model, session)

    # Add a new user with hashed password
    async def _add_user(self, data: dict) -> User:
        data = dict(data)  # copy, so the caller's dict isn't changed
        password = data.pop("password")  # never store the plain password
        user = self.model(
            **data,
            pass_hash=password_context.hash(password),
        )
        return await self._add(user)

    # Get a user by their email
    async def _get_by_email(self, email: str) -> User | None:
        # SELECT * FROM <table> WHERE email = :email   (first row or None)
        return await self.session.scalar(
            select(self.model).where(self.model.email == email)
        )

    # Validate the credentials and generate an access token
    async def _generate_token(self, email: str, password: str) -> str:
        user = await self._get_by_email(email)

        # Same error for "no such email" and "wrong password", so an attacker
        # can't use this endpoint to find out which emails have accounts.
        if user is None or not password_context.verify(password, user.pass_hash):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email or password is incorrect",
            )

        # What goes into the token: enough to find the user again later
        # (api/dependencies.py reads token_data["user"]["id"]).
        return generate_access_token(
            data={"user": {"name": user.name, "id": str(user.id)}}
        )
