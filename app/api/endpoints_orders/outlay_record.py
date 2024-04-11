from fastapi import APIRouter, Depends, status
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.models import Tutor, User, Engineer, Order, OutlayRecord, TypeOfPayment
from app.schemas.requests import OutlayRecordCreateRequest
from app.schemas.responses import OutlayRecordResponse, OutlayRecordBaseResponse, OutlayRecordTutorResponse
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
    response_model=list[OutlayRecordBaseResponse],
    status_code=status.HTTP_201_CREATED,
    description="Creates new Outlays.",
)
async def create_new_outlay_record(
    request_data: OutlayRecordCreateRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user)
) -> list[OutlayRecord]:
    data = jsonable_encoder(request_data)
    order = await session.scalar(select(Order).where(Order.order_number == data["order_number"]))
    engineer = await session.scalar(select(Engineer).where(Engineer.user_id == current_user.user_id))
    if order.engineers_number!=engineer.engineers_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USER_ACCESS_INVALID",
        )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Order with id {data['order_number']} not found")
    list_outlays = []
    for outlays in data["outlays"]:
        new_outlay = OutlayRecord(
            order_number=data["order_number"],
            name=outlays["name"],
            amount=outlays["amount"],
            cheque=outlays["cheque"],
            tp_of_pmt_id=outlays["tp_of_pmt_id"],
        )
        list_outlays.append(new_outlay)
        session.add(new_outlay)
    await session.commit()
    return list_outlays



@router.get(
    "/get_list/",
    response_model=list[OutlayRecordTutorResponse],
    status_code=status.HTTP_200_OK,
    description="Get list of outlays.",
)
async def get_all_outlays(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[OutlayRecordTutorResponse]:
    orders = await session.scalars(
        select(OutlayRecord.order_number).where(OutlayRecord.checked == False).group_by(OutlayRecord.order_number)
    )
    order = list(orders.all())
    data = []
    for o in order:
        outlay = await session.execute(
            select(
                OutlayRecord.name,
                OutlayRecord.amount,
                OutlayRecord.cheque,
                OutlayRecord.update_time,
                TypeOfPayment.type_of_payment,
                OutlayRecord.order_number,
                OutlayRecord.outlay_record_id,
            )
            .join(TypeOfPayment, OutlayRecord.tp_of_pmt_id == TypeOfPayment.tp_of_pmt_id)
            .where(OutlayRecord.order_number == o)
        )
        outlay_data = outlay.all()
        final_outlay = []
        for outlay in outlay_data:
            o_data = {
                "name": outlay[0],
                "amount": int(outlay[1]),
                "cheque": outlay[2],
                "update_time": outlay[3],
                "type_of_payment": outlay[4],
                "outlay_record_id": outlay[6]
            }
            final_outlay.append(o_data)
        res = {
            "order_number":outlay[5],
            "outlays": final_outlay
        }
        data.append(res)
    return data


@router.put(
    "/approve/{order_number}",
    status_code=status.HTTP_201_CREATED,
    description="approve outlay by tutor",
)
async def approve_outlay(
    order_number: int,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    check_role_tutor(current_user)
    outlay = await session.scalar(select(OutlayRecord).where(OutlayRecord.order_number == order_number))
    if not outlay:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THIS_ORDER_DOESNT_HAVE_OUTLAYS",
        )
    outlays = await session.execute(
        select(OutlayRecord.outlay_record_id).where(OutlayRecord.order_number == order_number)
    )
    o = outlays.all()
    for outlay in o:
        await session.execute(update(OutlayRecord).where(OutlayRecord.outlay_record_id == outlay[0]).values(checked = True))
    await session.execute(update(Order).where(Order.order_number == order_number).values(stage_of_order=4))
    await session.commit()

@router.delete(
    "/delete/{order_number}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="delete outlays by tutor",
)
async def delete_outlays(
    order_number: int,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    check_role_tutor(current_user)
    outlay = await session.scalar(select(OutlayRecord).where(OutlayRecord.order_number == order_number))
    if not outlay:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THIS_ORDER_DOESNT_HAVE_OUTLAYS",
        )
    outlays = await session.execute(select(OutlayRecord.outlay_record_id).where(OutlayRecord.order_number == order_number))
    o = outlays.all()
    for outlay in o:
        await session.execute(delete(OutlayRecord).where(OutlayRecord.outlay_record_id == outlay[0]))
    await session.commit()