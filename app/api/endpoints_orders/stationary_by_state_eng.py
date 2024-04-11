from fastapi import APIRouter, Depends, status
from sqlalchemy import select, delete, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from sqlalchemy.orm import aliased
from app.models import *
from app.schemas.requests import OrderCreateRequest, StationaryPutRequest, StationaryPriorityRequest
from app.schemas.responses import StationaryResponse, CurrentOrderTutorResponse


router = APIRouter()

def check_role_state_engineer(current_user):
    if current_user.role!="StateEngineer":
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

@router.put(
    "/take_stationary/{order_number}",
    status_code=status.HTTP_201_CREATED,
    description="state engineer takes stationary.",
)
async def take_stationary(
    order_number: int,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    check_role_state_engineer(current_user)
    stationary = await session.scalar(select(Stationary).where(Stationary.order_number == order_number))
    if not stationary:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THERE_IS_NO_STATIONARY_WITH_THIS_ORDER_NUMBER",
        )
    state_engineer = await session.scalar(select(StateEngineer).where(StateEngineer.name == current_user.user_name))
    await session.execute(update(Stationary).where(Stationary.order_number == order_number).values(state_engineers_number=state_engineer.state_engineers_number))
    await session.commit()


@router.put(
    "/add_amount/",
    status_code=status.HTTP_201_CREATED,
    description="state engineer add amount.",
)
async def take_stationary(
    data: StationaryPutRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    check_role_state_engineer(current_user)
    stationary = await session.scalar(select(Stationary).where(Stationary.order_number == data.order_number))
    if not stationary:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THERE_IS_NO_STATIONARY_WITH_THIS_ORDER_NUMBER",
        )
    await session.execute(update(Stationary).where(Stationary.order_number == data.order_number).values(amount=data.amount, done = True))
    await session.execute(update(Order).where(Order.order_number == data.order_number).values(stage_of_order=3))
    await session.commit()

