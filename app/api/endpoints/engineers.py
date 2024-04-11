# app/api/endpoints/pets.py

from fastapi import APIRouter, Depends, status
from sqlalchemy import select, delete, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.models import Tutor, User, Engineer, Order
from app.schemas.requests import EngineerCreateRequest
from app.schemas.responses import EngineerResponse, CurrentEngineerResponse

router = APIRouter()

def check_role_superuser(current_user):
    if current_user.role!="SuperUser" or current_user.role!="Tutor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USER_ACCESS_INVALID",
        )

def check_role_tutor(current_user):
    if current_user.role!="Tutor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USER_ACCESS_INVALID",
        )


@router.post(
    "/create",
    response_model=EngineerResponse,
    status_code=status.HTTP_201_CREATED,
    description="Creates new Engineer. Only for Tutors.",
)
async def create_new_engineer(
    data: EngineerCreateRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> Engineer:
    check_role_tutor(current_user)
    engineer1 = await session.scalar(select(Engineer).where(Engineer.name == data.name))
    engineer2 = await session.scalar(select(Engineer).where(Engineer.engineers_number == data.engineers_number))
    # a= 2/0
    if engineer1 or engineer2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ENGINEER_ALREADY_EXISTS",
        )
    new_engineer = Engineer(engineers_number=data.engineers_number, name=data.name, link=data.link)
    session.add(new_engineer)
    await session.commit()

    return new_engineer


@router.get(
    "/get_list/",
    response_model=list[EngineerResponse],
    status_code=status.HTTP_200_OK,
    description="Get list of engineers for Tutors",
)
async def get_all_engineers(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[Engineer]:

    check_role_tutor(current_user)
    engineers = await session.scalars(
        select(Engineer).where(Engineer.user_id != None).order_by(Engineer.name)
    )
    return list(engineers.all())


@router.delete(
    "/delete/{engineers_number}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete current engineer",
)
async def delete_current_engineer(
    engineers_number: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> None:
    check_role_tutor(current_user)
    engineer = await session.scalar(select(Engineer).where(Engineer.engineers_number == engineers_number))
    user = await session.scalar(select(User).where(User.user_name == engineer.name)) if engineer else None
    if user is None and engineer is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ENGINEER_HASNT_LOGGED_IN_YET",
        )
    if user is None and engineer is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THERE_IS_NO_ENGINEER_WITH_THIS_NUMBER",
        )

    await session.execute(update(Engineer).where(Engineer.engineers_number == engineers_number).values(user_id=None, name = engineer.name + "_deleted"))
    await session.flush()
    await session.execute(delete(User).where(User.user_name == engineer.name))
    await session.commit()


@router.get(
    "/get/{engineers_number}",
    response_model=CurrentEngineerResponse,
    status_code=status.HTTP_200_OK,
    description="Get list of engineers for Tutors",
)
async def get_current_engineers(
    engineers_number: int,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> CurrentEngineerResponse:

    check_role_tutor(current_user)
    engineer = await session.execute(
        select(Engineer.engineers_number, Engineer.name, Engineer.link).where(Engineer.engineers_number == engineers_number)
    )
    orders = await session.execute(
        select(Order.order_number, Order.stage_of_order).where(and_(Order.engineers_number == engineers_number, Order.done == False))
    )


    orders_data = orders.all()
    engineer_data = engineer.all()
    try:
        ord = []
        for order in orders_data:
            ord.append({"order_number": order[0], "stage_of_order": order[1]})
    except:
        ord = None
    try:
        data = {
            "engineers_number": engineer_data[0][0],
            "name": engineer_data[0][1],
            "link": engineer_data[0][2],
            "orders": ord
        }
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT_FOUND",
        )

    return data
