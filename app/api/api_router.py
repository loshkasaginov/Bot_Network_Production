from fastapi import APIRouter

from app.api import api_messages

from app.api.endpoints import auth, users, tutors, engineers, state_engineers, penalty
from app.api.endpoints_orders import orders_by_tutor, agreement, prepayment, outlay_record, report, stationary,\
    get_order_by_stage, stationary_by_state_eng, stages_tutor

auth_router = APIRouter()
auth_router.include_router(auth.router, prefix="/auth", tags=["auth"])

api_router = APIRouter(
    responses={
        401: {
            "description": "No `Authorization` access token header, token is invalid or user removed",
            "content": {
                "application/json": {
                    "examples": {
                        "not authenticated": {
                            "summary": "No authorization token header",
                            "value": {"detail": "Not authenticated"},
                        },
                        "invalid token": {
                            "summary": "Token validation failed, decode failed, it may be expired or malformed",
                            "value": {"detail": "Token invalid: {detailed error msg}"},
                        },
                        "removed user": {
                            "summary": api_messages.JWT_ERROR_USER_REMOVED,
                            "value": {"detail": api_messages.JWT_ERROR_USER_REMOVED},
                        },
                    }
                }
            },
        },
    }
)
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tutors.router, prefix="/tutors", tags=["tutors"])
api_router.include_router(engineers.router, prefix="/engineers", tags=["engineers"])
api_router.include_router(state_engineers.router, prefix="/state_engineers", tags=["state_engineers"])
api_router.include_router(orders_by_tutor.router, prefix="/orders", tags=["orders"])
api_router.include_router(agreement.router, prefix="/agreement", tags=["agreement"])
api_router.include_router(prepayment.router, prefix="/prepayment", tags=["prepayment"])
api_router.include_router(outlay_record.router, prefix="/outlay_record", tags=["outlay_record"])
api_router.include_router(report.router, prefix="/report", tags=["report"])
api_router.include_router(stationary.router, prefix="/stationary", tags=["stationary"])
api_router.include_router(penalty.router, prefix="/penalty", tags=["penalty"])
api_router.include_router(get_order_by_stage.router, prefix="/get_order_by_stage", tags=["get_order_by_stage"])
api_router.include_router(stationary_by_state_eng.router, prefix="/stationary_by_state_eng", tags=["stationary_by_state_eng"])
api_router.include_router(stages_tutor.router, prefix="/stages_tutor", tags=["stages_tutor"])