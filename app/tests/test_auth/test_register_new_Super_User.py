from fastapi import status
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import api_messages
from app.main import app
from app.models import User


async def test_register_new_superuser_status_code(
    client: AsyncClient,
) -> None:
    response = await client.post(
        app.url_path_for("register_new_superuser"),
        json={
            "user_name": "test_login",
            "password": "061203-13a",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED


async def test_register_new_superuser_creates_record_in_db(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    await client.post(
        app.url_path_for("register_new_superuser"),
        json={
            "user_name": "test_login",
            "password": "061203-13a",
        },
    )

    user_count = await session.scalar(
        select(func.count()).where(User.user_name == "test_login")
    )
    assert user_count == 1


async def test_register_new_superuser_cannot_create_already_created_superuser(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    user = User(
        user_name="test_login",
        hashed_password="061203-13a",
    )
    session.add(user)
    await session.commit()

    response = await client.post(
        app.url_path_for("register_new_superuser"),
        json={
            "user_name": "test_login",
            "password": "061203-13a",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "USERNAME_ALREADY_USED"}
