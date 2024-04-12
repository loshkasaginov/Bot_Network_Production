from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
from datetime import datetime

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


class OrderCreateRequest(BaseRequest):
    engineers_name: str
    order_number: int



class ForkCreate(BaseRequest):
    amount: int
    description: str

class RejectionCreate(BaseRequest):
    amount: int
    description: str

class AgreementCreate(BaseRequest):
    forks: List[ForkCreate] = []
    rejection: Optional[RejectionCreate] = None

class AgreementCreateRequest(BaseRequest):
    order_number: int
    amount: int
    agreement_details: AgreementCreate


class PrepaymentCreateRequest(BaseRequest):
    order_number: int
    amount: int
    tp_of_pmt_id: int


class OutlayRecordCreate(BaseRequest):
    name: str
    amount: int
    cheque: str
    tp_of_pmt_id: int

class OutlayRecordCreateRequest(BaseRequest):
    order_number: int
    outlays: List[OutlayRecordCreate] = None


class ReportCreateRequest(BaseRequest):
    order_number: int
    all_amount: int
    clear_amount: int
    photo_of_agreement: Optional[str]
    advance_payment: int
    tp_of_pmt_id: int

class StationaryPutRequest(BaseRequest):
    order_number: int
    amount: int

class StationaryPriorityRequest(BaseRequest):
    order_number: int
    priority: int

class StationaryCreateRequest(BaseRequest):
    order_number: int
    photo: str
    date: datetime
    description: str

class PenaltyCreateRequest(BaseRequest):
    engineers_number: int
    amount: int
    description: str

class GetOrderByDateReqeust(BaseModel):
    start_time:datetime
    end_time:datetime