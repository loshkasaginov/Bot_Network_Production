# app/tests/test_pets/test_pets.py

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models import User, Tutor, Engineer



async def test_create_new_engineer_by_tutor(
    client: AsyncClient, default_user_headers: dict[str, str], default_user: User
) -> None:
    default_user.role = "Tutor"
    response = await client.post(
        app.url_path_for("create_new_engineer"),
        headers=default_user_headers,
        json={"engineers_number": 123,
              "link": "test_link",
              "name": "test_engineer"
              },
    )
    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result["engineers_number"] == 123
    assert result["link"] == "test_link"
    assert result["name"] == "test_engineer"



async def get_all_engineers_by_tutor(
    client: AsyncClient,
    default_user_headers: dict[str, str],
    session: AsyncSession,
    default_user: User
) -> None:
    default_user.role = "Tutor"
    engineer1 = Engineer( engineers_number=1, link="test_link1", name="test_engineer1")
    engineer2 = Engineer( engineers_number=2, link="test_link2", name="test_engineer2")

    session.add(engineer1)
    session.add(engineer2)
    await session.commit()

    response = await client.get(
        app.url_path_for("get_all_engineers"),
        headers=default_user_headers,
    )
    assert response.status_code == status.HTTP_200_OK

    assert response.json() == [
        {
            "engineers_number": engineer1.engineers_number,
            "link": engineer1.link,
            "name": engineer1.name
        },
        {
            "engineers_number": engineer2.engineers_number,
            "link": engineer2.link,
            "name": engineer2.name
        },
    ]

async def test_create_new_engineer_not_by_tutor(
    client: AsyncClient, default_user_headers: dict[str, str], default_user: User
) -> None:
    default_user.role = "test"
    response = await client.post(
        app.url_path_for("create_new_engineer"),
        headers=default_user_headers,
        json={"engineers_number": 123,
              "link": "test_link",
              "name": "test_engineer"
              },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "USER_ACCESS_INVALID"}


async def get_all_engineers_not_by_tutor(
    client: AsyncClient,
    default_user_headers: dict[str, str],
    default_user: User,
    session: AsyncSession,
) -> None:
    default_user.role = "test"
    engineer1 = Tutor(tutors_number=1, link="test_link1", name="test_engineer1")
    engineer2 = Tutor(tutors_number=2, link="test_link2", name="test_engineer2")

    session.add(engineer1)
    session.add(engineer2)
    await session.commit()

    response = await client.get(
        app.url_path_for("get_all_engineers"),
        headers=default_user_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "USER_ACCESS_INVALID"}