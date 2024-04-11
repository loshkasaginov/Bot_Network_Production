
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import pytest
from datetime import datetime, timedelta
from app.main import app
from app.models import User, Tutor, Engineer, Order, Stationary, TypeOfPayment


async def test_create_new_stationary(
    client: AsyncClient,
    default_user_headers: dict[str, str],
    session: AsyncSession,
    default_user: User
) -> None:
    default_user.role = "Engineer"
    default_user.user_name = "test_engineer"
    tutor = Tutor(tutors_number=1, link="test_link", name="test_tutor")
    engineer = Engineer(engineers_number=1, link="test_link", name="test_engineer", user_id=default_user.user_id)
    tp_of_pmt = TypeOfPayment(tp_of_pmt_id=1, type_of_payment="cash")
    session.add(tutor)
    session.add(engineer)
    session.add(tp_of_pmt)
    await session.commit()
    order = Order(order_number=1,tutors_number=1,engineers_number=1)
    session.add(order)
    await session.commit()
    date_str = "2023-04-04"
    penalty_date = datetime.strptime(date_str, "%Y-%m-%d") + timedelta(hours=0, minutes=0, seconds=0,
                                                                   milliseconds=0)
    date = penalty_date.isoformat() + 'Z'
    response = await client.post(
        app.url_path_for("create_new_stationary"),
        headers=default_user_headers,
        json={
      "order_number":1,
      "photo":"photo",
      "description":"description",
      "date": date,
    }
    )
    assert response.status_code == status.HTTP_201_CREATED
    # result = response.json()
    # assert result["order_number"] == 1
