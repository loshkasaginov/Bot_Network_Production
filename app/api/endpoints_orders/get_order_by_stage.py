from fastapi import APIRouter, Depends, status
from sqlalchemy import select, delete, update, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.models import  Tutor, User, Engineer, Order, Stationary, StateEngineer
from app.schemas.requests import OrderCreateRequest
from app.schemas.responses import OrderResponse, OrderTutorShortResponse, StationaryResponse, StationaryTutorResponse


router = APIRouter()

def check_role_tutor(current_user):
    if current_user.role!="Tutor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USER_ACCESS_INVALID",
        )

def check_role_state_engineer(current_user):
    if current_user.role!="StateEngineer":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USER_ACCESS_INVALID",
        )


@router.get(
    "/agreement",
    response_model=list[OrderResponse],
    status_code=status.HTTP_200_OK,
    description="Get agreement orders for current Engineer.",
)
async def get_agreement_order_engineer(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[Order]:
    engineer = await session.scalar(select(Engineer).where(Engineer.name == current_user.user_name))
    orders = await session.scalars(
        select(Order).where(and_(Order.stage_of_order==0 , Order.engineers_number == engineer.engineers_number))
    )
    return list(orders.all())

@router.get(
    "/prepayment",
    response_model=list[OrderResponse],
    status_code=status.HTTP_200_OK,
    description="Get prepayment orders for current Engineer.",
)
async def get_prepayment_order_engineer(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[Order]:
    engineer = await session.scalar(select(Engineer).where(Engineer.name == current_user.user_name))
    orders = await session.scalars(
        select(Order).where(and_(Order.stage_of_order==1 , Order.engineers_number == engineer.engineers_number))
    )
    return list(orders.all())



@router.get(
    "/outlay_record",
    response_model=list[OrderResponse],
    status_code=status.HTTP_200_OK,
    description="Get outlay_record orders for current Engineer.",
)
async def get_outlay_order_engineer(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[Order]:
    engineer = await session.scalar(select(Engineer).where(Engineer.name == current_user.user_name))

    orders = await session.scalars(
        select(Order)
        .where(and_(or_(Order.stage_of_order==3, Order.stage_of_order==2) , Order.engineers_number == engineer.engineers_number))
    )
    return list(orders.all())


@router.get(
    "/report",
    response_model=list[OrderResponse],
    status_code=status.HTTP_200_OK,
    description="Get report orders for current Engineer.",
)
async def get_report_order_engineer(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[Order]:
    engineer = await session.scalar(select(Engineer).where(Engineer.name == current_user.user_name))
    orders = await session.scalars(
        select(Order).where(and_(or_(Order.stage_of_order==3, Order.stage_of_order==2, Order.stage_of_order==4) , Order.engineers_number == engineer.engineers_number))
    )
    return list(orders.all())

@router.get(
    "/stationary",
    response_model=list[OrderResponse],
    status_code=status.HTTP_200_OK,
    description="Get stationary orders for current Engineer.",
)
async def get_stationary_order_engineer(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[Order]:
    engineer = await session.scalar(select(Engineer).where(Engineer.name == current_user.user_name))
    orders = await session.scalars(
        select(Order).where(and_(Order.stage_of_order==2 , Order.engineers_number == engineer.engineers_number))
    )
    return list(orders.all())


@router.get(
    "/stationary/not_assigned/state_engineer",
    response_model=list[StationaryResponse],
    status_code=status.HTTP_200_OK,
    description="Get not_assigned stationary for current StateEngineer.",
)
async def get_not_assigned_stationary_state_engineer(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[StationaryResponse]:
    check_role_state_engineer(current_user)
    stationary = await session.execute(
        select(Order.order_number,
               Stationary.stationary_id,
               Stationary.priority,
               Stationary.date,
               Stationary.photo,
               Stationary.description,
               Engineer.name,
               )
        .join(Order, Order.order_number == Stationary.order_number)
        .join(Engineer, Engineer.engineers_number == Order.engineers_number)
        .where(and_(Stationary.state_engineers_number==None , Stationary.done == False))
    )
    state = stationary.all()
    data = []
    for s in state:
        data.append({
            "order_number": s[0],
            "stationary_id": s[1],
            "priority": s[2],
            "date": s[3],
            "photo": s[4],
            "description": s[5],
            "name": s[6],
        })
    return data

@router.get(
    "/stationary/assigned/state_engineer",
    response_model=list[StationaryResponse],
    status_code=status.HTTP_200_OK,
    description="Get assigned stationary for current StateEngineer.",
)
async def get_assigned_stationary_state_engineer(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[Order]:
    check_role_state_engineer(current_user)
    state_engineer = await session.scalar(select(StateEngineer).where(StateEngineer.name == current_user.user_name))
    stationary = await session.execute(
        select(Order.order_number,
               Stationary.stationary_id,
               Stationary.priority,
               Stationary.date,
               Stationary.photo,
               Stationary.description,
               Engineer.name,
               )
        .join(Order, Order.order_number == Stationary.order_number)
        .join(Engineer, Engineer.engineers_number == Order.engineers_number)
        .where(and_(Stationary.state_engineers_number == state_engineer.state_engineers_number, Stationary.done == False))
    )
    state = stationary.all()
    data = []
    for s in state:
        data.append({
            "order_number": s[0],
            "stationary_id": s[1],
            "priority": s[2],
            "date": s[3],
            "photo": s[4],
            "description": s[5],
            "name": s[6],
        })
    return data


@router.get(
    "/stationary/tutor",
    response_model=list[StationaryTutorResponse],
    status_code=status.HTTP_200_OK,
    description="Get orders in stationary for tutor.",
)
async def get_stationary_tutor(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[StationaryTutorResponse]:
    check_role_tutor(current_user)
    stationary = await session.execute(
        select(Order.engineers_number,
               Stationary.state_engineers_number,
               Stationary.stationary_id,
               Stationary.priority,
               Stationary.photo,
               Stationary.description,
               Order.order_number,
               Stationary.update_time,
               Stationary.amount,
               Stationary.date,
               )
        .join(Order, Order.order_number == Stationary.order_number)
        .where(Stationary.done == False)
    )
    stationary_data = stationary.all()
    final_data = []
    for s in stationary_data:
        data = {
            "engineers_number": s[0],
            "state_engineers_number": s[1],
            "stationary_id": s[2],
            "priority": s[3],
            "photo": s[4],
            "description": s[5],
            "order_number": s[6],
            "update_time": s[7],
            "amount": s[8],
            "date": s[9],
        }
        final_data.append(data)


    return final_data

