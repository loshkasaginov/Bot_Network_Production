import secrets
import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import api_messages, deps
from app.core.config import get_settings
from app.core.security.jwt import create_jwt_token
from app.core.security.password import (
    DUMMY_PASSWORD,
    get_password_hash,
    verify_password,
)
from app.models import RefreshToken, User, Tutor, Engineer, StateEngineer
from app.schemas.requests import RefreshTokenRequest, UserCreateRequest
from app.schemas.responses import AccessTokenResponse, UserResponse

router = APIRouter()

ACCESS_TOKEN_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: {
        "description": "Invalid username or password",
        "content": {
            "application/json": {"example": {"detail": api_messages.PASSWORD_INVALID}}
        },
    },
}

REFRESH_TOKEN_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: {
        "description": "Refresh token expired or is already used",
        "content": {
            "application/json": {
                "examples": {
                    "refresh token expired": {
                        "summary": api_messages.REFRESH_TOKEN_EXPIRED,
                        "value": {"detail": api_messages.REFRESH_TOKEN_EXPIRED},
                    },
                    "refresh token already used": {
                        "summary": api_messages.REFRESH_TOKEN_ALREADY_USED,
                        "value": {"detail": api_messages.REFRESH_TOKEN_ALREADY_USED},
                    },
                }
            }
        },
    },
    404: {
        "description": "Refresh token does not exist",
        "content": {
            "application/json": {
                "example": {"detail": api_messages.REFRESH_TOKEN_NOT_FOUND}
            }
        },
    },
}


@router.post(
    "/access-token",
    response_model=AccessTokenResponse,
    responses=ACCESS_TOKEN_RESPONSES,
    description="OAuth2 compatible token, get an access token for future requests using username and password",
)
async def login_access_token(
    session: AsyncSession = Depends(deps.get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> AccessTokenResponse:
    user = await session.scalar(select(User).where(User.user_name == form_data.username))

    if user is None:
        # this is naive method to not return early
        verify_password(form_data.password, DUMMY_PASSWORD)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=api_messages.PASSWORD_INVALID,
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=api_messages.PASSWORD_INVALID,
        )

    jwt_token = create_jwt_token(user_id=user.user_id)

    refresh_token = RefreshToken(
        user_id=user.user_id,
        refresh_token=secrets.token_urlsafe(32),
        exp=int(time.time() + get_settings().security.refresh_token_expire_secs),
    )
    session.add(refresh_token)
    await session.commit()

    return AccessTokenResponse(
        access_token=jwt_token.access_token,
        expires_at=jwt_token.payload.exp,
        refresh_token=refresh_token.refresh_token,
        refresh_token_expires_at=refresh_token.exp,
    )


@router.post(
    "/refresh-token",
    response_model=AccessTokenResponse,
    responses=REFRESH_TOKEN_RESPONSES,
    description="OAuth2 compatible token, get an access token for future requests using refresh token",
)
async def refresh_token(
    data: RefreshTokenRequest,
    session: AsyncSession = Depends(deps.get_session),
) -> AccessTokenResponse:
    token = await session.scalar(
        select(RefreshToken)
        .where(RefreshToken.refresh_token == data.refresh_token)
        .with_for_update(skip_locked=True)
    )

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=api_messages.REFRESH_TOKEN_NOT_FOUND,
        )
    elif time.time() > token.exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=api_messages.REFRESH_TOKEN_EXPIRED,
        )
    elif token.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=api_messages.REFRESH_TOKEN_ALREADY_USED,
        )

    token.used = True
    session.add(token)

    jwt_token = create_jwt_token(user_id=token.user_id)

    refresh_token = RefreshToken(
        user_id=token.user_id,
        refresh_token=secrets.token_urlsafe(32),
        exp=int(time.time() + get_settings().security.refresh_token_expire_secs),
    )
    session.add(refresh_token)
    await session.commit()

    return AccessTokenResponse(
        access_token=jwt_token.access_token,
        expires_at=jwt_token.payload.exp,
        refresh_token=refresh_token.refresh_token,
        refresh_token_expires_at=refresh_token.exp,
    )


@router.post(
    "/register",
    response_model=UserResponse,
    description="Create new user",
    status_code=status.HTTP_201_CREATED,
)
async def register_new_user(
    new_user: UserCreateRequest,
    session: AsyncSession = Depends(deps.get_session),
) -> User:
    user = await session.scalar(select(User).where(User.user_name == new_user.user_name))
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USERNAME_ALREADY_USED",
        )

    user = User(
        user_name=new_user.user_name,
        hashed_password=get_password_hash(new_user.password),
    )
    session.add(user)

    try:
        await session.commit()
    except IntegrityError:  # pragma: no cover
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USERNAME_ALREADY_USED",
        )

    return user



@router.post(
    "/register/SuperUser",
    response_model=UserResponse,
    description="Create new SuperUser",
    status_code=status.HTTP_201_CREATED,
)
async def register_new_superuser(
    new_user: UserCreateRequest,
    session: AsyncSession = Depends(deps.get_session),
) -> User:
    user = await session.scalar(select(User).where(User.user_name == new_user.user_name))
    if user is not None:
        if verify_password(new_user.password, user.hashed_password):
            return user
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USERNAME_ALREADY_USED"
        )
    if new_user.password!="test_password":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=api_messages.PASSWORD_INVALID,
        )
    user = User(
        user_name=new_user.user_name,
        hashed_password=get_password_hash(new_user.password),
        role="SuperUser"
    )
    session.add(user)

    try:
        await session.commit()
    except IntegrityError:  # pragma: no cover
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=api_messages.USERNANE_ALREADY_USED,
        )

    return user


@router.post(
    "/register/tutor",
    response_model=UserResponse,
    description="register new tutor",
    status_code=status.HTTP_201_CREATED,
)
async def register_new_tutor(
    new_user: UserCreateRequest,
    session: AsyncSession = Depends(deps.get_session),
) -> User:
    user = await session.scalar(select(User).where(User.user_name == new_user.user_name))
    tutor = await session.scalar(select(Tutor).where(Tutor.name == new_user.user_name))
    if user is not None:
        if verify_password( new_user.password, user.hashed_password):
            return user
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USERNAME_ALREADY_USED",
        )
    if tutor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USERNAME_INVALID",
        )
    user = User(
        user_name=new_user.user_name,
        hashed_password=get_password_hash(new_user.password),
        role="Tutor"
    )
    session.add(user)
    await session.flush()
    tutor.user_id = user.user_id
    try:
        await session.commit()
    except IntegrityError:  # pragma: no cover
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=api_messages.USERNANE_ALREADY_USED,
        )

    return user


@router.post(
    "/register/engineer",
    response_model=UserResponse,
    description="Create new engineer",
    status_code=status.HTTP_201_CREATED,
)
async def register_new_engineer(
    new_user: UserCreateRequest,
    session: AsyncSession = Depends(deps.get_session),
) -> User:
    user = await session.scalar(select(User).where(User.user_name == new_user.user_name))
    engineer = await session.scalar(select(Engineer).where(Engineer.name == new_user.user_name))
    if user is not None:
        if verify_password(new_user.password, user.hashed_password):
            return user
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USERNAME_ALREADY_USED",
        )
    if engineer is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USERNAME_INVALID",
        )
    user = User(
        user_name=new_user.user_name,
        hashed_password=get_password_hash(new_user.password),
        role="Engineer"
    )
    session.add(user)
    await session.flush()
    engineer.user_id = user.user_id
    try:
        await session.commit()
    except IntegrityError:  # pragma: no cover
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=api_messages.USERNANE_ALREADY_USED,
        )

    return user


@router.post(
    "/register/state_engineer",
    response_model=UserResponse,
    description="Create new state engineer",
    status_code=status.HTTP_201_CREATED,
)
async def register_new_state_engineer(
    new_user: UserCreateRequest,
    session: AsyncSession = Depends(deps.get_session),
) -> User:
    user = await session.scalar(select(User).where(User.user_name == new_user.user_name))
    state_engineer = await session.scalar(select(StateEngineer).where(StateEngineer.name == new_user.user_name))
    if user is not None:
        if verify_password(new_user.password, user.hashed_password):
            return user
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USERNAME_ALREADY_USED",
        )
    if state_engineer is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USERNAME_INVALID",
        )
    user = User(
        user_name=new_user.user_name,
        hashed_password=get_password_hash(new_user.password),
        role="StateEngineer"
    )
    session.add(user)
    await session.flush()
    state_engineer.user_id = user.user_id
    try:
        await session.commit()
    except IntegrityError:  # pragma: no cover
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=api_messages.USERNANE_ALREADY_USED,
        )

    return user