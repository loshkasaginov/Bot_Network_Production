from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional, List

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


class OrderResponse(BaseResponse):
    order_number: int
    stage_of_order: int

class CurrentEngineerResponse(EngineerResponse):
    orders: Optional[List[OrderResponse]]

class StationaryBaseResponse(BaseResponse):
    order_number: int
class StationaryResponse(BaseResponse):
    order_number: int
    name:Optional[str]
    stationary_id: int
    priority: int
    date: Optional[datetime]
    photo: str
    description:str


class StationaryTutorResponse(BaseResponse):
    order_number: int
    engineers_number: int
    state_engineers_number: Optional[int]
    stationary_id: int
    amount: Optional[int]
    date: Optional[datetime]
    priority: int
    photo: str
    description:str
    update_time: datetime


class CurrentStateEngineerResponse(EngineerResponse):
    orders: Optional[List[StationaryResponse]]

class CurrentStateEngineerOrderTutorResponse(BaseResponse):
    order_number:int
    stage_of_order:int

class CurrentStateEngineerTutorResponse(BaseResponse):
    engineers_number:int
    name:str
    link:str
    orders: Optional[List[CurrentStateEngineerOrderTutorResponse]]



class StateEngineerResponse(RoleResponse):
    state_engineers_number: int




class ForkResponse(BaseResponse):
    amount: int
    description: str

class RejectionResponse(BaseResponse):
    amount: int
    description: str
class Agreement(BaseResponse):
    forks: List[ForkResponse] = []
    rejection: Optional[RejectionResponse] = None


class AgreementBaseResponse(BaseResponse):
    amount: int

class AgreementResponse(BaseResponse):
    amount: int
    update_time: datetime
    agreement_details: Agreement

class AgreementTutorResponse(BaseResponse):
    amount: int
    order_number: int
    update_time: datetime
    agreement_details: Agreement

class TypeOfPayment(BaseResponse):
    type_of_payment: str

class PrepaymentResponse(BaseResponse):
    amount: int
    update_time: datetime
    type_of_payment: str

class PrepaymentTutorResponse(BaseResponse):
    order_number: int
    amount: int
    update_time: datetime
    type_of_payment: str


class OutlayRecordBaseResponse(BaseResponse):
    name: str
class OutlayRecordResponse(BaseResponse):
    name: str
    amount: int
    cheque: str
    update_time: datetime
    type_of_payment: str

class OutlayResponse(BaseResponse):
    outlay_record_id: int
    name: str
    amount: int
    cheque: str
    update_time: datetime
    type_of_payment: str
class OutlayRecordTutorResponse(BaseResponse):
    order_number: int
    outlays: List[OutlayResponse]


class ReportResponse(BaseResponse):
    all_amount: int
    clear_amount: int
    update_time: datetime
    photo_of_agreement: Optional[str]
    advance_payment: int
    type_of_payment: str

class ReportTutorResponse(ReportResponse):
    order_number: int

class ReportBaseResponse(BaseResponse):
    all_amount: int



class PenaltyResponse(BaseResponse):
    engineers_number: int

class PenaltyUserResponse(BaseResponse):
    amount: int
    description: str
    update_time: datetime


class OrderTutorShortResponse(BaseResponse):
    order_number: int
    engineers_number: int
    name: str
    stage_of_order: int
    update_time: datetime

class CurrentOrderDetails(BaseResponse):
    agreement: Optional[AgreementResponse]
    prepayment: Optional[PrepaymentResponse]
    stationary: Optional[StationaryTutorResponse]
    outlay_record: Optional[List[OutlayRecordResponse]]
    report: Optional[ReportResponse]

class CurrentOrderTutorResponse(BaseResponse):
    order_number: int
    engineers_number: int
    engineers_name: str
    stage_of_order: int
    update_time: datetime
    details: CurrentOrderDetails

class PrepaymentBaseResponse(BaseResponse):
    amount: int


class AllStagesCountResponse(BaseResponse):
    agreements: int
    prepayments: int
    outlays: int
    reports: int

class ReportPhotoResponse(BaseResponse):
    photo:Optional[str]