# app/tests/test_pets/test_pets.py

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models import User, Tutor



async def test_create_new_tutor_by_superuser(
    client: AsyncClient, default_user_headers: dict[str, str], default_user: User
) -> None:
    default_user.role = "SuperUser"
    response = await client.post(
        app.url_path_for("create_new_tutor"),
        headers=default_user_headers,
        json={"tutors_number": 123,
              "link": "test_link",
              "name": "test_tutor"
              },
    )
    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result["tutors_number"] == 123
    assert result["link"] == "test_link"
    assert result["name"] == "test_tutor"



async def get_all_tutors_by_superuser(
    client: AsyncClient,
    default_user_headers: dict[str, str],
    session: AsyncSession,
    default_user: User
) -> None:
    # default_user.role = "SuperUserde"
    tutor1 = Tutor( tutors_number=1, link="test_link1", name="test_tutor1")
    tutor2 = Tutor( tutors_number=2, link="test_link2", name="test_tutor2")

    session.add(tutor1)
    session.add(tutor2)
    await session.commit()

    response = await client.get(
        app.url_path_for("get_all_tutors"),
        headers=default_user_headers,
    )
    assert response.status_code == status.HTTP_200_OK

    assert response.json() == [
        {
            "tutors_number": tutor1.tutors_number,
            "link": tutor1.link,
            "name": tutor1.name
        },
        {
            "tutors_number": tutor2.tutors_number,
            "link": tutor2.link,
            "name": tutor2.name
        },
    ]

async def test_create_new_tutor_not_by_superuser(
    client: AsyncClient, default_user_headers: dict[str, str], default_user: User
) -> None:
    default_user.role = "Tutor"
    response = await client.post(
        app.url_path_for("create_new_tutor"),
        headers=default_user_headers,
        json={"tutors_number": 123,
              "link": "test_link",
              "name": "test_tutor"
              },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "USER_ACCESS_INVALID"}


async def get_all_tutors_not_by_superuser(
    client: AsyncClient,
    default_user_headers: dict[str, str],
    default_user: User,
    session: AsyncSession,
) -> None:
    default_user.role = "SuperUser"
    tutor1 = Tutor(tutors_number=1, link="test_link1", name="test_tutor1")
    tutor2 = Tutor(tutors_number=2, link="test_link2", name="test_tutor2")

    session.add(tutor1)
    session.add(tutor2)
    await session.commit()

    response = await client.get(
        app.url_path_for("get_all_tutors"),
        headers=default_user_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "USER_ACCESS_INVALID"}