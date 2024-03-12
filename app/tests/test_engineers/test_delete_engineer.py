# app/tests/test_pets/test_pets.py

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models import User, Tutor, Engineer



async def test_delete_new_engineer_by_tutor(
    client: AsyncClient,
    default_user_headers: dict[str, str],
    default_user: User,
    session: AsyncSession,
) -> None:
    default_user.role = "Tutor"
    engineer = Engineer(
        engineers_number = 123,
        link = "test_link",
        name = "test_engineer",
    )
    user = User(
        user_name="test_engineer",
        hashed_password="bla",
    )
    session.add(user)
    session.add(engineer)
    await session.commit()
    response = await client.delete(
        app.url_path_for("delete_current_engineer", engineers_name="test_engineer"),
        headers=default_user_headers,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
#    assert response.status_code == status.HTTP_204_NO_CONTENT
#     assert response.json() == {"detail": "USER_ACCESS_INVALID"}