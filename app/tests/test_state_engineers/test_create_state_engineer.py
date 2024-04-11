# app/tests/test_pets/test_pets.py

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models import User, Tutor, StateEngineer



async def test_create_new_state_engineer_by_tutor(
    client: AsyncClient, default_user_headers: dict[str, str], default_user: User
) -> None:
    default_user.role = "Tutor"
    response = await client.post(
        app.url_path_for("create_new_state_engineer"),
        headers=default_user_headers,
        json={"state_engineers_number": 123,
              "link": "test_link",
              "name": "test_state_engineer"
              },
    )
    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    # print(response.status_code, result)
    assert result["state_engineers_number"] == 123
    assert result["link"] == "test_link"
    assert result["name"] == "test_state_engineer"



async def get_all_state_engineers_by_tutor(
    client: AsyncClient,
    default_user_headers: dict[str, str],
    session: AsyncSession,
    default_user: User
) -> None:
    default_user.role = "Tutor"
    state_engineer1 = StateEngineer( state_engineers_number=1, link="test_link1", name="test_state_engineer1")
    state_engineer2 = StateEngineer( state_engineers_number=2, link="test_link2", name="test_state_engineer2")

    session.add(state_engineer1)
    session.add(state_engineer2)
    await session.commit()

    response = await client.get(
        app.url_path_for("get_all_state_engineers"),
        headers=default_user_headers,
    )
    assert response.status_code == status.HTTP_200_OK

    assert response.json() == [
        {
            "state_engineers_number": state_engineer1.state_engineers_number,
            "link": state_engineer1.link,
            "name": state_engineer1.name
        },
        {
            "state_engineers_number": state_engineer2.state_engineers_number,
            "link": state_engineer2.link,
            "name": state_engineer2.name
        },
    ]

async def test_create_new_state_engineer_not_by_tutor(
    client: AsyncClient, default_user_headers: dict[str, str], default_user: User
) -> None:
    default_user.role = "test"
    response = await client.post(
        app.url_path_for("create_new_state_engineer"),
        headers=default_user_headers,
        json={"state_engineers_number": 123,
              "link": "test_link",
              "name": "test_state_engineer"
              },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "USER_ACCESS_INVALID"}


async def get_all_state_engineers_not_by_tutor(
    client: AsyncClient,
    default_user_headers: dict[str, str],
    default_user: User,
    session: AsyncSession,
) -> None:
    default_user.role = "test"
    state_engineer1 = StateEngineer(state_engineers_number=1, link="test_link1", name="test_state_engineer1")
    state_engineer2 = StateEngineer(state_engineers_number=2, link="test_link2", name="test_state_engineer2")

    session.add(state_engineer1)
    session.add(state_engineer2)
    await session.commit()

    response = await client.get(
        app.url_path_for("get_all_state_engineers"),
        headers=default_user_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "USER_ACCESS_INVALID"}