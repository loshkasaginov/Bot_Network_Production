# app/tests/test_pets/test_pets.py

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
# from app.tests.confest import
from app.main import app
from app.models import User, Tutor, StateEngineer



async def test_delete_new_state_engineer_by_tutor(
    client: AsyncClient,
    default_user_headers: dict[str, str],
    default_user: User,
    session: AsyncSession,
) -> None:
    default_user.role = "Tutor"
    user = User(
        user_name="test_state_engineer",
        hashed_password="bla",
        user_id='2c266ae1-629c-44ec-879a-ecf79b608111',
    )
    state_engineer = StateEngineer(
        state_engineers_number = 123,
        link = "test_link",
        name = "test_state_engineer",
        user_id='2c266ae1-629c-44ec-879a-ecf79b608111',
    )

    session.add(user)
    await session.commit()
    session.add(state_engineer)
    await session.commit()
    response = await client.delete(
        app.url_path_for("delete_current_state_engineer", state_engineers_number=123),
        headers=default_user_headers,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
#    assert response.status_code == status.HTTP_204_NO_CONTENT
#     assert response.json() == {"detail": "USER_ACCESS_INVALID"}