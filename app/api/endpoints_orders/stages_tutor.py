from fastapi import APIRouter, Depends, status
from sqlalchemy import select, delete, update, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.models import  *
from app.schemas.requests import OrderCreateRequest
from app.schemas.responses import AllStagesCountResponse, OrderTutorShortResponse, StationaryResponse, StationaryTutorResponse


router = APIRouter()


@router.get(
    "/stages",
    response_model=AllStagesCountResponse,
    status_code=status.HTTP_200_OK,
    description="Get count of all stages for tutor.",
)
async def get_all_stages_tutor(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> AllStagesCountResponse:
    engineer = await session.scalar(select(Engineer).where(Engineer.name == current_user.user_name))
    agreements = await session.execute(
        select(func.count()).select_from(
            select(Agreement).where(Agreement.checked == False).subquery()
        )
    )
    prepayments = await session.execute(
        select(func.count()).select_from(
            select(Prepayment).where(Prepayment.checked == False).subquery()
        )
    )
    outlays = await session.execute(
        select(func.count()).select_from(
            select(OutlayRecord).where(OutlayRecord.checked == False).subquery()
        )
    )
    reports = await session.execute(
        select(func.count()).select_from(
            select(Report).where(Report.checked == False).subquery()
        )
    )

    agreements_count = agreements.scalar()
    prepayment_count = prepayments.scalar()
    outlay_count = outlays.scalar()
    report_count = reports.scalar()
    data = {
        "agreements": agreements_count,
        "prepayments": prepayment_count,
        "outlays": outlay_count,
        "reports": report_count,
    }
    return data