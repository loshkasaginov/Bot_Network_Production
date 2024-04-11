
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import pytest
from app.main import app
from app.models import User, Tutor, Engineer, Order, Report, TypeOfPayment


async def test_create_new_agreement(
    client: AsyncClient,
    default_user_headers: dict[str, str],
    session: AsyncSession,
    default_user: User
) -> None:
    default_user.role = "Engineer"
    default_user.user_name = "test_engineer"
    tutor = Tutor(tutors_number=1, link="test_link", name="test_tutor")
    engineer = Engineer(engineers_number=1, link="test_link", name="test engineer")
    tp_of_pmt = TypeOfPayment(tp_of_pmt_id=1, type_of_payment="cash")

    session.add(tutor)
    session.add(engineer)
    session.add(tp_of_pmt)
    order = Order(order_number=1,tutors_number=1,engineers_number=1)
    session.add(order)
    await session.commit()

    response = await client.post(
        app.url_path_for("create_new_report"),
        headers=default_user_headers,
        json={
      "order_number":1,
      "all_amount":2,
        "clear_amount":1,
        "photo_of_agreement": None,
        "advance_payment":2,
        "tp_of_pmt_id":1,
    }
    )
    assert response.status_code == status.HTTP_201_CREATED
    # result = response.json()
    # assert result["order_number"] == 1
