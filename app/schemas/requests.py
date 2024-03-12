from pydantic import BaseModel, EmailStr


class BaseRequest(BaseModel):
    # may define additional fields or config shared across requests
    pass


class RefreshTokenRequest(BaseRequest):
    refresh_token: str


class UserUpdatePasswordRequest(BaseRequest):
    password: str


class UserCreateRequest(BaseRequest):
    user_name: str
    password: str


class RoleCreateRequest(BaseRequest):
    link: str
    name: str

class SuperUserCreateRequest(UserCreateRequest):
    pass

class TutorCreateRequest(RoleCreateRequest):
    tutors_number: int



class EngineerCreateRequest(RoleCreateRequest):
    engineers_number: int


class StateEngineerCreateRequest(RoleCreateRequest):
    state_engineers_number: int
