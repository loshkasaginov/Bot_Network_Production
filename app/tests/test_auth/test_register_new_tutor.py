from fastapi import status
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import api_messages
from app.main import app
from app.models import User, Tutor


async def test_register_new_tutor_correct_name_status_code(
    client: AsyncClient,
    session: AsyncSession,

) -> None:
    tutor = Tutor(tutors_number=1, link="test_link", name="test_tutor")

    session.add(tutor)
    response = await client.post(
        app.url_path_for("register_new_tutor"),
        json={
            "user_name": tutor.name,
            "password": "test_password",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED


async def test_register_new_correct_name_tutor_creates_record_in_db(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    tutor = Tutor(tutors_number=1, link="test_link", name="test_tutor")
    session.add(tutor)
    await client.post(
        app.url_path_for("register_new_tutor"),
        json={
            "user_name": tutor.name,
            "password": "test_password",
        },
    )

    tutor_count = await session.scalar(
        select(func.count()).where(Tutor.name == "test_tutor")
    )
    assert tutor_count == 1


async def test_register_new_correct_name_tutor_cannot_create_already_created_tutor(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    tutor = Tutor(tutors_number=1, link="test_link", name="test_tutor")
    session.add(tutor)
    user = User(
        user_name=tutor.name,
        hashed_password="test_password",
    )
    session.add(user)
    await session.commit()

    response = await client.post(
        app.url_path_for("register_new_tutor"),
        json={
            "user_name": tutor.name,
            "password": "test_password",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "USERNAME_ALREADY_USED"}
