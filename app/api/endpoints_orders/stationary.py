from fastapi import APIRouter, Depends, status
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.models import Tutor, User, Engineer, Order, Stationary
from app.schemas.requests import StationaryCreateRequest, StationaryPriorityRequest
from app.schemas.responses import StationaryResponse, StationaryBaseResponse
from fastapi.encoders import jsonable_encoder


router = APIRouter()



@router.post(
    "/create",
    response_model=StationaryBaseResponse,
    status_code=status.HTTP_201_CREATED,
    description="Creates new Stationary.",
)
async def create_new_stationary(
    data: StationaryCreateRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user)
) -> Stationary:
    order = await session.scalar(select(Order).where(Order.order_number == data.order_number))
    engineer = await session.scalar(select(Engineer).where(Engineer.user_id == current_user.user_id))
    if order.engineers_number!=engineer.engineers_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USER_ACCESS_INVALID",
        )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Order with id {data.order_number} not found")
    new_stationary = Stationary(
        order_number=data.order_number,
        photo=data.photo,
        date=data.date,
        description=data.description,
    )
    session.add(new_stationary)
    await session.execute(update(Order).where(Order.order_number == data.order_number).values(stage_of_order=-1))
    await session.commit()
    return new_stationary


@router.put(
    "/add_priority/",
    status_code=status.HTTP_201_CREATED,
    description="state engineer takes stationary.",
)
async def take_stationary(
    data: StationaryPriorityRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    check_role_tutor(current_user)
    stationary = session.scalar(select(Stationary).where(Stationary.order_number==data.order_number))
    if not stationary:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THIS_ORDER_DOES_NOT_HAVE_STATIONARY",
        )
    await session.execute(update(Stationary).where(Stationary.order_number == data.order_number).values(priority=data.priority,))
    await session.commit()