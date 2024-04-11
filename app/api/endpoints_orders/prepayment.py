from fastapi import APIRouter, Depends, status
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.models import Tutor, User, Engineer, Order, Prepayment, TypeOfPayment
from app.schemas.requests import PrepaymentCreateRequest
from app.schemas.responses import PrepaymentBaseResponse, PrepaymentTutorResponse
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
    response_model=PrepaymentBaseResponse,
    status_code=status.HTTP_201_CREATED,
    description="Creates new Prepayment.",
)
async def create_new_prepayment(
    data: PrepaymentCreateRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user)
) -> Prepayment:
    order = await session.scalar(select(Order).where(Order.order_number == data.order_number))
    engineer = await session.scalar(select(Engineer).where(Engineer.user_id == current_user.user_id))
    if order.engineers_number!=engineer.engineers_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USER_ACCESS_INVALID",
        )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Order with id {data.order_number} not found")
    new_prepayment = Prepayment(order_number=data.order_number, amount=data.amount, tp_of_pmt_id=data.tp_of_pmt_id)
    session.add(new_prepayment)
    await session.commit()
    return new_prepayment



@router.get(
    "/get_list/",
    response_model=list[PrepaymentTutorResponse],
    status_code=status.HTTP_200_OK,
    description="Get list of prepayments.",
)
async def get_all_prepayments(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[PrepaymentTutorResponse]:
    orders = await session.scalars(
        select(Prepayment.order_number).where(Prepayment.checked == False )
    )
    order = list(orders.all())
    data = []
    for p in order:
        prepayment = await session.execute(
            select(
                Prepayment.amount,
                Prepayment.update_time,
                TypeOfPayment.type_of_payment,
                Prepayment.order_number
            )
            .join(TypeOfPayment, Prepayment.tp_of_pmt_id == TypeOfPayment.tp_of_pmt_id)
            .where(Prepayment.order_number == p)
        )
        prepayment_data = prepayment.all()[0]
        prep_data = {
            "order_number": prepayment_data[3],
            "amount": prepayment_data[0],
            "update_time": prepayment_data[1],
            "type_of_payment": prepayment_data[2],
        }
        data.append(prep_data)

    return data


@router.put(
    "/approve/{order_number}",
    status_code=status.HTTP_201_CREATED,
    description="approve prepayment by tutor",
)
async def approve_prepayment(
    order_number: int,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    check_role_tutor(current_user)
    prepayment = await session.scalar(select(Prepayment).where(Prepayment.order_number == order_number))
    if not prepayment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THIS_ORDER_DOESNT_HAVE_PREPAYMENT",
        )
    await session.execute(update(Prepayment).where(Prepayment.order_number == order_number).values(checked = True,))
    await session.execute(update(Order).where(Order.order_number == order_number).values(stage_of_order = 2, ))
    await session.commit()


@router.delete(
    "/delete/{order_number}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="delete prepayment by tutor",
)
async def delete_prepayment(
    order_number: int,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    check_role_tutor(current_user)
    prepayment = await session.scalar(select(Prepayment).where(Prepayment.order_number == order_number))
    if not prepayment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THIS_ORDER_DOESNT_HAVE_PREPAYMENT",
        )
    prepayment = await session.execute(select(Prepayment.prepayment_id).where(Prepayment.order_number == order_number))
    p = prepayment.all()[0]
    await session.execute(delete(Prepayment).where(Prepayment.prepayment_id == p[0]))
    await session.commit()