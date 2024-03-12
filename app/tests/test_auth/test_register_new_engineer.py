from fastapi import status
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import api_messages
from app.main import app
from app.models import User, Tutor, Engineer


async def test_register_new_engineer_correct_name_status_code(
    client: AsyncClient,
    session: AsyncSession,

) -> None:
    engineer = Engineer(engineers_number=1, link="test_link", name="test_engineer")

    session.add(engineer)
    response = await client.post(
        app.url_path_for("register_new_engineer"),
        json={
            "user_name": engineer.name,
            "password": "test_password",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED


async def test_register_new_engineer_correct_name_engineer_creates_record_in_db(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    engineer = Engineer(engineers_number=1, link="test_link", name="test_engineer")
    session.add(engineer)
    await client.post(
        app.url_path_for("register_new_engineer"),
        json={
            "user_name": engineer.name,
            "password": "test_password",
        },
    )

    engineer_count = await session.scalar(
        select(func.count()).where(Engineer.name == "test_engineer")
    )
    assert engineer_count == 1


async def test_register_new_correct_name_engineer_cannot_create_already_created_engineer(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    engineer = Engineer(engineers_number=1, link="test_link", name="test_engineer")
    session.add(engineer)
    user = User(
        user_name=engineer.name,
        hashed_password="test_password",
    )
    session.add(user)
    await session.commit()

    response = await client.post(
        app.url_path_for("register_new_engineer"),
        json={
            "user_name": engineer.name,
            "password": "test_password",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "USERNAME_ALREADY_USED"}
