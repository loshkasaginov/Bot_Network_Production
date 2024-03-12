# app/api/endpoints/pets.py

from fastapi import APIRouter, Depends, status
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.models import Tutor, User
from app.schemas.requests import TutorCreateRequest
from app.schemas.responses import TutorResponse

router = APIRouter()

def check_role_superuser(current_user):
    if current_user.role!="SuperUser":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USER_ACCESS_INVALID",
        )


@router.post(
    "/create/tutor/",
    response_model=TutorResponse,
    status_code=status.HTTP_201_CREATED,
    description="Creates new Tutor. Only for SuperUsers.",
)
async def create_new_tutor(
    data: TutorCreateRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> Tutor:
    check_role_superuser(current_user)
    new_tutor = Tutor(tutors_number=data.tutors_number, name=data.name, link=data.link)
    session.add(new_tutor)
    await session.commit()

    return new_tutor


@router.get(
    "/get_list/",
    response_model=list[TutorResponse],
    status_code=status.HTTP_200_OK,
    description="Get list of tutors for currently SuperUsers.",
)
async def get_all_tutors(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[Tutor]:
    check_role_superuser(current_user)
    tutors = await session.scalars(
        select(Tutor).where(Tutor.user_id == current_user.user_id).order_by(Tutor.name)
    )
    return list(tutors.all())


@router.delete(
    "/delete/{tutor_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete current tutor",
)
async def delete_current_tutor(
    tutor_name: str,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> None:
    check_role_superuser(current_user)
    user = await session.scalar(select(User).where(User.user_name == tutor_name))
    tutor = await session.scalar(select(Tutor).where(Tutor.name == tutor_name))
    if user is None and tutor is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TUTOR_HASNT_LOGGED_IN_YET",
        )
    if user is None and tutor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THERE_IS_NO_TUTOR_WITH_THIS_NAME",
        )
    tutor.user_id=None
    await session.execute(update(Tutor).where(Tutor.name == tutor_name))
    await session.flush()
    await session.execute(delete(User).where(User.user_name == tutor_name))
    await session.commit()