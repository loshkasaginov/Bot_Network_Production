from fastapi import APIRouter, Depends, status
from sqlalchemy import select, delete, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.api import deps
from sqlalchemy.orm import aliased
from app.models import *
from fastapi_cache.decorator import cache
from app.schemas.requests import OrderCreateRequest, GetOrderByDateReqeust
from app.schemas.responses import OrderResponse, OrderTutorShortResponse, CurrentOrderTutorResponse, ReportTutorResponse


router = APIRouter()


def check_role_tutor(current_user):
    if current_user.role!="Tutor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USER_ACCESS_INVALID",
        )


@router.post(
    "/create",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    description="Creates new Order. Only for Tutors.",
)
async def create_new_order(
    data: OrderCreateRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> Order:
    check_role_tutor(current_user)
    engineer = await session.scalar(select(Engineer).where(Engineer.name == data.engineers_name))
    tutor = await session.scalar(select(Tutor).where(Tutor.name == current_user.user_name))
    order = await session.scalar(select(Order).where(Order.order_number == data.order_number))
    if order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ORDER_ALREADY_EXISTS",
        )
    if not engineer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ENGINEER_NOT_FOUNT",
        )
    new_order = Order(order_number=data.order_number,
                      tutors_number=tutor.tutors_number,
                      engineers_number=engineer.engineers_number,
                      )
    session.add(new_order)
    await session.commit()

    return new_order



@router.get(
    "/get/short",
    response_model=list[OrderTutorShortResponse],
    status_code=status.HTTP_200_OK,
    description="Get all active orders.",
)
async def get_orders_tutor(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[OrderTutorShortResponse]:
    check_role_tutor(current_user)
    result = await session.execute(
        select(Order.order_number, Order.engineers_number, Order.stage_of_order, Order.update_time , Engineer.name)
        .join(Engineer, Engineer.engineers_number == Order.engineers_number)
        .where( Order.done == False)
    )
    return list(result.all())


@router.get(
    "/get/by_date",
    response_model=list[ReportTutorResponse],
    status_code=status.HTTP_200_OK,
    description="Get list of reports by date.",
)
async def get_all_reports_by_date(
        # data: GetOrderByDateReqeust,
        session: AsyncSession = Depends(deps.get_session),
        current_user: User = Depends(deps.get_current_user),
        start_time: datetime = Query(..., description="Start time for filtering orders"),
        end_time: datetime = Query(..., description="End time for filtering orders"),
) -> list[ReportTutorResponse]:
    check_role_tutor(current_user)
    orders = await session.scalars(
        select(Report.order_number).where(and_(Report.checked == True, Report.update_time.between(start_time, end_time)))
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


@router.get(
    "/get/{order_number}",
    response_model=CurrentOrderTutorResponse,
    status_code=status.HTTP_200_OK,
    description="Get current order tutor.",
)
@cache(expire=60)
async def get_current_order_tutor(
    order_number: int,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> CurrentOrderTutorResponse:
    check_role_tutor(current_user)
    order = await session.scalar(select(Order).where(Order.order_number==order_number))
    if not order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THERE_IS_NO_ORDER_WITH_THIS_NUMBER",
        )

    main_info = await session.execute(
        select(Order.order_number, Order.engineers_number, Engineer.name, Order.stage_of_order, Order.update_time )
        .join(Engineer, Engineer.engineers_number == Order.engineers_number)
        .where(Order.order_number == int(order_number))
    )

    res_data = main_info.all()[0]
    agreement = await session.execute(
        select(
            Order.order_number,
            Agreement.amount,
            Fork.description,
            Fork.amount,
            Rejection.description,
            Rejection.amount,
            Agreement.update_time,
        )
        .join(Agreement, Agreement.order_number == Order.order_number)
        .join(Fork, Agreement.agreement_id == Fork.agreement_id)
        .outerjoin(Rejection, Rejection.agreement_id == Agreement.agreement_id)
        .where(Order.order_number == order_number)
    )

    try :
        agreement_data = agreement.all()
        forks = []
        for agr in agreement_data:
            fork_data = {
                "description": agr[2],
                "amount": agr[3]
            }
            forks.append(fork_data)
        if agreement_data[0][4]:
            rejection = {
                "description": agreement_data[0][4],
                "amount": agreement_data[0][5]
            }
        else:
            rejection = None
        agr_data = {
            "amount": agreement_data[0][1],
            "update_time": agreement_data[0][6],
            "agreement_details": {
                "forks" : forks,
                "rejection": rejection
            }
        }
    except:
        agr_data = None

    try:
        prepayment = await session.execute(
            select(
                Prepayment.amount,
                Prepayment.update_time,
                TypeOfPayment.type_of_payment
            )
            .join(TypeOfPayment, Prepayment.tp_of_pmt_id == TypeOfPayment.tp_of_pmt_id)
            .where(Prepayment.order_number == order_number)
        )
        prepayment_data = prepayment.all()[0]
        prep_data = {
            "amount": prepayment_data[0],
            "update_time": prepayment_data[1],
            "type_of_payment": prepayment_data[2],
        }
    except:
        prep_data = None


    try:
        outlay = await session.execute(
            select(
                OutlayRecord.name,
                OutlayRecord.amount,
                OutlayRecord.cheque,
                OutlayRecord.update_time,
                TypeOfPayment.type_of_payment
            )
            .join(TypeOfPayment, OutlayRecord.tp_of_pmt_id == TypeOfPayment.tp_of_pmt_id)
            .where(OutlayRecord.order_number == order_number)
        )
        outlay_data = outlay.all()
        final_outlay = []
        for outlay in outlay_data:
            o_data = {
                "name":outlay[0],
                "amount": int(outlay[1]),
                "cheque": outlay[2],
                "update_time": outlay[3],
                "type_of_payment": outlay[4]
            }
            final_outlay.append(o_data)
    except:
        final_outlay = None

    try:
        report = await session.execute(
            select(
                Report.all_amount,
                Report.clear_amount,
                Report.advance_payment,
                Report.photo_of_agreement,
                Report.update_time,
                TypeOfPayment.type_of_payment
            )
            .join(TypeOfPayment, Report.tp_of_pmt_id == TypeOfPayment.tp_of_pmt_id)
            .where(Report.order_number == order_number)
        )
        report_data = report.all()[0]

        r_data = {
            "all_amount":report_data[0],
            "clear_amount": int(report_data[1]),
            "advance_payment": report_data[2],
            "photo_of_agreement": report_data[3],
            "update_time": report_data[4],
            "type_of_payment": report_data[5]
        }

    except:
        r_data = None
    try:
        stationary = await session.execute(
            select(Order.engineers_number,
                   Stationary.state_engineers_number,
                   Stationary.stationary_id,
                   Stationary.priority,
                   Stationary.photo,
                   Stationary.description,
                   Order.order_number,
                   Stationary.update_time,
                   Stationary.amount,
                   Stationary.date,
                   )
            .join(Stationary, Stationary.order_number == Order.order_number)
            .where(Order.order_number == order_number)
        )
        s = stationary.all()[0]

        final_data = {
                "engineers_number": s[0],
                "state_engineers_number": s[1],
                "stationary_id": s[2],
                "priority": s[3],
                "photo": s[4],
                "description": s[5],
                "order_number": s[6],
                "update_time": s[7],
                "amount": s[8],
                "date": s[9],
                "name": None,
            }
    except:
        final_data = None

    data = {
        "order_number": res_data[0],
        "engineers_number": res_data[1],
        "engineers_name": res_data[2],
        "stage_of_order": res_data[3],
        "update_time": res_data[4],
        "details": {
            "agreement":  agr_data,
            "prepayment": prep_data,
            "stationary": final_data,
            "outlay_record": final_outlay,
            "report": r_data,

        }
        }
    # order_data = result.scalars().first()
    # if order_data is None:
    #     raise HTTPException(status_code=404, detail="Заказ не найден")

    return data