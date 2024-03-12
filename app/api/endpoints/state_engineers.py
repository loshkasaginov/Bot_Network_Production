from fastapi import APIRouter, Depends, status
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.models import Tutor, User, StateEngineer
from app.schemas.requests import StateEngineerCreateRequest
from app.schemas.responses import StateEngineerResponse

router = APIRouter()

def check_role_superuser(current_user):
    if current_user.role!="SuperUser":
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
    response_model=StateEngineerResponse,
    status_code=status.HTTP_201_CREATED,
    description="Creates new StateEngineer. Only for Tutors.",
)
async def create_new_state_engineer(
    data: StateEngineerCreateRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> StateEngineer:
    check_role_tutor(current_user)
    new_state_engineer = StateEngineer(state_engineers_number=data.state_engineers_number, name=data.name, link=data.link)
    session.add(new_state_engineer)
    await session.commit()

    return new_state_engineer


@router.get(
    "/get_list/",
    response_model=list[StateEngineerResponse],
    status_code=status.HTTP_200_OK,
    description="Get list of state engineers for currently SuperUsers/Tutors",
)
async def get_all_state_engineers(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[StateEngineer]:
    check_role_superuser(current_user)
    state_engineers = await session.scalars(
        select(StateEngineer).where(StateEngineerResponse.user_id == current_user.user_id).order_by(StateEngineer.name)
    )
    return list(state_engineers.all())


@router.delete(
    "/delete/{state_engineers_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete current state engineer",
)
async def delete_current_state_engineer(
    state_engineers_name: str,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> None:
    check_role_tutor(current_user)
    user = await session.scalar(select(User).where(User.user_name == state_engineers_name))
    state_engineer = await session.scalar(select(StateEngineer).where(StateEngineer.name == state_engineers_name))
    if user is None and state_engineer is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="STATE_ENGINEER_HASNT_LOGGED_IN_YET",
        )
    if user is None and state_engineer is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THERE_IS_NO_STATE_ENGINEER_WITH_THIS_NAME",
        )
    state_engineer.user_id=None
    await session.execute(update(StateEngineer).where(StateEngineer.name == state_engineers_name))
    await session.flush()
    await session.execute(delete(User).where(User.user_name == state_engineers_name))
    await session.commit()