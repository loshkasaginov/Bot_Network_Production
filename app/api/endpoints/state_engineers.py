from fastapi import APIRouter, Depends, status
from sqlalchemy import select, delete, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.models import Tutor, User, StateEngineer, Stationary, Order
from app.schemas.requests import StateEngineerCreateRequest
from app.schemas.responses import StateEngineerResponse, CurrentStateEngineerResponse, CurrentStateEngineerTutorResponse

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
    state_engineer1 = await session.scalar(select(StateEngineer).where(StateEngineer.name == data.name))
    state_engineer2 = await session.scalar(select(StateEngineer).where(StateEngineer.state_engineers_number == data.state_engineers_number))
    if state_engineer2 or state_engineer1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="STATE_ENGINEER_ALREADY_EXISTS",
        )
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
    check_role_tutor(current_user)
    state_engineers = await session.scalars(
        select(StateEngineer)
    )
    return list(state_engineers.all())


@router.delete(
    "/delete/{state_engineers_number}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete current state engineer",
)
async def delete_current_state_engineer(
    state_engineers_number: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> None:
    check_role_tutor(current_user)

    state_engineer = await session.scalar(select(StateEngineer).where(StateEngineer.state_engineers_number == state_engineers_number))
    user = await session.scalar(select(User).where(User.user_id == state_engineer.user_id))
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
    await session.execute(update(StateEngineer).where(StateEngineer.name == state_engineer.name).values(user_id=None, name = state_engineer.name + "_deleted"))
    await session.flush()
    await session.execute(delete(User).where(User.user_name == state_engineer.name))
    await session.commit()

@router.get(
    "/get/{state_engineers_number}",
    response_model=CurrentStateEngineerTutorResponse,
    status_code=status.HTTP_200_OK,
    description="Get current state_engineers for currently Tutors",
)
async def get_current_state_engineers(
    state_engineers_number: int,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> CurrentStateEngineerTutorResponse:

    check_role_tutor(current_user)
    state_engineer = await session.execute(
        select(StateEngineer.state_engineers_number, StateEngineer.name, StateEngineer.link).where(StateEngineer.state_engineers_number == state_engineers_number)
    )
    stationary = await session.execute(
        select(Stationary.order_number, Order.stage_of_order)
        .where(and_(Stationary.state_engineers_number == state_engineers_number, Stationary.done == False))
        .join(Order, Stationary.order_number == Order.order_number)
    )


    orders_data = stationary.all()
    engineer_data = state_engineer.all()
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
