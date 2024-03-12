# app/api/endpoints/pets.py

from fastapi import APIRouter, Depends, status
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.models import Tutor, User, Engineer
from app.schemas.requests import EngineerCreateRequest
from app.schemas.responses import EngineerResponse

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
    new_engineer = Engineer(engineers_number=data.engineers_number, name=data.name, link=data.link)
    session.add(new_engineer)
    await session.commit()

    return new_engineer


@router.get(
    "/get_list/",
    response_model=list[EngineerResponse],
    status_code=status.HTTP_200_OK,
    description="Get list of engineers for currently SuperUsers/Tutors",
)
async def get_all_engineers(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[Engineer]:
    check_role_superuser(current_user)
    engineers = await session.scalars(
        select(Engineer).where(Engineer.user_id == current_user.user_id).order_by(Engineer.name)
    )
    return list(engineers.all())


@router.delete(
    "/delete/{engineers_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete current engineer",
)
async def delete_current_engineer(
    engineers_name: str,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> None:
    check_role_tutor(current_user)
    user = await session.scalar(select(User).where(User.user_name == engineers_name))
    engineer = await session.scalar(select(Engineer).where(Engineer.name == engineers_name))
    if user is None and engineer is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ENGINEER_HASNT_LOGGED_IN_YET",
        )
    if user is None and engineer is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THERE_IS_NO_ENGINEER_WITH_THIS_NAME",
        )
    engineer.user_id=None
    await session.execute(update(Engineer).where(Engineer.name == engineers_name))
    await session.flush()
    await session.execute(delete(User).where(User.user_name == engineers_name))
    await session.commit()