
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import pytest
from app.main import app
from app.models import User, Tutor, Engineer, Order, Penalty


async def test_create_new_penalty(
    client: AsyncClient,
    default_user_headers: dict[str, str],
    session: AsyncSession,
    default_user: User
) -> None:
    default_user.role = "Tutor"
    default_user.user_name = "test_engineer"
    engineer = Engineer(engineers_number=1, link="test_link", name="test engineer")
    session.add(engineer)
    await session.commit()

    response = await client.post(
        app.url_path_for("create_new_penalty"),
        headers=default_user_headers,
        json={
      "engineers_number":1,
      "amount":2,
        "description":"lol",
    }
    )
    assert response.status_code == status.HTTP_201_CREATED
    # result = response.json()
    # assert result["order_number"] == 1
