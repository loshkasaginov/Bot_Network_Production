from pydantic import BaseModel, ConfigDict, EmailStr


class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AccessTokenResponse(BaseResponse):
    token_type: str = "Bearer"
    access_token: str
    expires_at: int
    refresh_token: str
    refresh_token_expires_at: int


class UserResponse(BaseResponse):
    user_id: str
    user_name: str


class SuperuserUserResponse(UserResponse):
    pass

class RoleResponse(BaseResponse):
    link: str
    name: str

class TutorResponse(RoleResponse):
    tutors_number: int


class EngineerResponse(RoleResponse):
    engineers_number: int



class StateEngineerResponse(RoleResponse):
    state_engineers_number: int
