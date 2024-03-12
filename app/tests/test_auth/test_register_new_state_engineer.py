from fastapi import status
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import api_messages
from app.main import app
from app.models import User, Tutor, StateEngineer


async def test_register_new_state_engineer_correct_name_status_code(
    client: AsyncClient,
    session: AsyncSession,

) -> None:
    state_engineer = StateEngineer(state_engineers_number=1, link="test_link", name="test_state_engineer")

    session.add(state_engineer)
    response = await client.post(
        app.url_path_for("register_new_state_engineer"),
        json={
            "user_name": state_engineer.name,
            "password": "test_password",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED


async def test_register_new_state_engineer_correct_name_state_engineer_creates_record_in_db(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    state_engineer = StateEngineer(state_engineers_number=1, link="test_link", name="test_state_engineer")
    session.add(state_engineer)
    await client.post(
        app.url_path_for("register_new_state_engineer"),
        json={
            "user_name": state_engineer.name,
            "password": "test_password",
        },
    )

    state_engineer_count = await session.scalar(
        select(func.count()).where(StateEngineer.name == "test_state_engineer")
    )
    assert state_engineer_count == 1


async def test_register_new_correct_name_state_engineer_cannot_create_already_created_state_engineer(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    state_engineer = StateEngineer(state_engineers_number=1, link="test_link", name="test_state_engineer")
    session.add(state_engineer)
    user = User(
        user_name=state_engineer.name,
        hashed_password="test_password",
    )
    session.add(user)
    await session.commit()

    response = await client.post(
        app.url_path_for("register_new_state_engineer"),
        json={
            "user_name": state_engineer.name,
            "password": "test_password",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "USERNAME_ALREADY_USED"}
