from fastapi import APIRouter, Depends, status
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.models import Tutor, User, Engineer, Order, Penalty
from app.schemas.requests import PenaltyCreateRequest
from app.schemas.responses import PenaltyResponse, PenaltyUserResponse
from fastapi.encoders import jsonable_encoder


router = APIRouter()


def check_role_tutor(current_user):
    if current_user.role!="Tutor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USER_ACCESS_INVALID",
        )


@router.post(
    "/create",
    response_model=PenaltyResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create new Penalty.",
)
async def create_new_penalty(
    data: PenaltyCreateRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user)
) -> Penalty:
    check_role_tutor(current_user)
    engineer = await session.scalar(select(Engineer).where(Engineer.engineers_number == data.engineers_number))
    if not engineer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THERE_IS_NO_ENGINEER_WITH_THIS_NUMBER",
        )
    new_penalty = Penalty(
        engineers_number=data.engineers_number,
        amount=data.amount,
        description=data.description,
    )
    session.add(new_penalty)
    await session.commit()
    return new_penalty


@router.get(
    "/engineer",
    response_model=list[PenaltyUserResponse],
    status_code=status.HTTP_200_OK,
    description="Get penalties for engineer.",
)
async def get_penalties_engineer(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[PenaltyUserResponse]:
    # check_role_tutor(current_user)
    engineer = await session.scalar(select(Engineer).where(Engineer.name == current_user.user_name))
    if not engineer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THERE_IS_NOT_ENGINEER",
        )
    penalty = await session.execute(
        select(Penalty.amount,
               Penalty.description,
               Penalty.update_time,
               )
        .where(Penalty.engineers_number == engineer.engineers_number)
    )
    data = []
    for p in penalty:
        data.append({
            "amount": p[0],
            "description": p[1],
            "update_time": p[2],
        })
    return data

@router.get(
    "/tutor/{engineers_number}",
    response_model=list[PenaltyUserResponse],
    status_code=status.HTTP_200_OK,
    description="Get penalties for tutor.",
)
async def get_penalties_tutor(
    engineers_number:int,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[PenaltyUserResponse]:
    check_role_tutor(current_user)
    engineer = await session.scalar(select(Engineer).where(Engineer.engineers_number == engineers_number))
    if not engineer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THERE_IS_NO_ENGINEER_WITH_THIS_NUMBER",
        )
    penalty = await session.execute(
        select(Penalty.amount,
               Penalty.description,
               Penalty.update_time,
               )
        .where(Penalty.engineers_number == engineers_number)
    )
    data = []
    for p in penalty:
        data.append({
            "amount": p[0],
            "description": p[1],
            "update_time": p[2],
        })
    return data