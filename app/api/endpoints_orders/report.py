from fastapi import APIRouter, Depends, status
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.models import Tutor, User, Engineer, Order, Report, TypeOfPayment
from app.schemas.requests import ReportCreateRequest
from app.schemas.responses import ReportBaseResponse, ReportTutorResponse, ReportPhotoResponse
from fastapi.encoders import jsonable_encoder


router = APIRouter()

def check_role_tutor(current_user):
    if current_user.role!="Tutor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USER_ACCESS_INVALID",
        )

@router.post(
    "/create",
    response_model=ReportBaseResponse,
    status_code=status.HTTP_201_CREATED,
    description="Creates new Report.",
)
async def create_new_report(
    data: ReportCreateRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user)
) -> Report:
    order = await session.scalar(select(Order).where(Order.order_number == data.order_number))
    engineer = await session.scalar(select(Engineer).where(Engineer.user_id == current_user.user_id))
    report = await session.scalar(select(Report).where(Report.order_number == data.order_number))
    if report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report already created",
        )
    if order.engineers_number!=engineer.engineers_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USER_ACCESS_INVALID",
        )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Order with id {data.order_number} not found")
    new_report = Report(
        order_number=data.order_number,
        all_amount=data.all_amount,
        clear_amount=data.clear_amount,
        photo_of_agreement=data.photo_of_agreement,
        advance_payment=data.advance_payment,
        tp_of_pmt_id=data.tp_of_pmt_id
    )
    session.add(new_report)
    await session.commit()
    return new_report


@router.get(
    "/get_list/",
    response_model=list[ReportTutorResponse],
    status_code=status.HTTP_200_OK,
    description="Get list of reports.",
)
async def get_all_reports(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[ReportTutorResponse]:
    orders = await session.scalars(
        select(Report.order_number).where(Report.checked == False )
    )
    order = list(orders.all())
    data = []
    for r in order:
        report = await session.execute(
            select(
                Report.all_amount,
                Report.clear_amount,
                Report.advance_payment,
                Report.photo_of_agreement,
                Report.update_time,
                TypeOfPayment.type_of_payment,
                Report.order_number,
            )
            .join(TypeOfPayment, Report.tp_of_pmt_id == TypeOfPayment.tp_of_pmt_id)
            .where(Report.order_number == r)
        )
        report_data = report.all()[0]

        r_data = {
            "all_amount": report_data[0],
            "clear_amount": int(report_data[1]),
            "advance_payment": report_data[2],
            "photo_of_agreement": report_data[3],
            "update_time": report_data[4],
            "type_of_payment": report_data[5],
            "order_number": report_data[6]
        }
        data.append(r_data)
    return data


@router.put(
    "/approve/{order_number}",
    status_code=status.HTTP_201_CREATED,
    description="approve prepayment by tutor",
)
async def approve_report(
    order_number: int,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    check_role_tutor(current_user)
    report = session.scalar(select(Report).where(Report.order_number == order_number))
    if not report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THIS_ORDER_DOESNT_HAVE_REPORT",
        )
    await session.execute(update(Report).where(Report.order_number == order_number).values(checked = True,))
    await session.execute(update(Order).where(Order.order_number == order_number).values(stage_of_order = 5, done = True))
    await session.commit()

@router.delete(
    "/delete/{order_number}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="delete prepayment by tutor",
)
async def delete_agreement(
    order_number: int,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    check_role_tutor(current_user)
    report = session.scalar(select(Report).where(Report.order_number == order_number))
    if not report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THIS_ORDER_DOESNT_HAVE_REPORT",
        )
    report = await session.execute(select(Report.report_id).where(Report.order_number == order_number))
    r = report.all()[0]
    await session.execute(delete(Report).where(Report.report_id == r[0]))
    await session.commit()


@router.get(
    "/get/photo/{order_number}",
    response_model=ReportPhotoResponse,
    status_code=status.HTTP_200_OK,
    description="get order photo by tutor",
)
async def get_photo(
    order_number: int,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
)->ReportPhotoResponse:
    check_role_tutor(current_user)
    report = session.scalar(select(Report).where(Report.order_number == order_number))
    if not report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THIS_ORDER_DOESNT_HAVE_REPORT",
        )
    photo = await session.scalar(select(Report.photo_of_agreement).where(Report.order_number == order_number))
    data = {
        "photo": photo
    }
    return data