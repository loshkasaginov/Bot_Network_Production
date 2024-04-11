from fastapi import APIRouter, Depends, status
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.models import Tutor, User, Engineer, Order, Agreement, Fork, Rejection, Report
from app.schemas.requests import AgreementCreateRequest
from app.schemas.responses import AgreementBaseResponse, AgreementTutorResponse
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
    response_model=AgreementBaseResponse,
    status_code=status.HTTP_201_CREATED,
    description="Creates new Agreement.",
)
async def create_new_agreement(
    request_data: AgreementCreateRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user)
) -> Agreement:
    data = jsonable_encoder(request_data)
    order = await session.scalar(select(Order).where(Order.order_number == data["order_number"]))
    engineer = await session.scalar(select(Engineer).where(Engineer.user_id == current_user.user_id))


    if not order or not engineer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Order with id {data['order_number']} not found")
    new_agreement = Agreement(
        order_number=data["order_number"],
        amount=data["amount"]
    )
    if order.engineers_number!=engineer.engineers_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USER_ACCESS_INVALID",
        )

    session.add(new_agreement)
    await session.flush()

    for fork_data in data["agreement_details"]["forks"]:
        new_fork = Fork(
            agreement_id=new_agreement.agreement_id,
            amount=fork_data["amount"],
            description=fork_data["description"]
        )
        session.add(new_fork)

    if data["agreement_details"]["rejection"]:
        new_rejection = Rejection(
            agreement_id=new_agreement.agreement_id,
            amount=data["agreement_details"]["rejection"]["amount"],
            description=data["agreement_details"]["rejection"]["description"]
        )
        session.add(new_rejection)
        await session.execute(update(Order).where(Order.order_number == data["order_number"]).values(stage_of_order=5, done=True))
        new_report = Report(
            order_number=data["order_number"],
            all_amount=data["agreement_details"]["rejection"]["amount"],
            clear_amount=data["agreement_details"]["rejection"]["amount"],
            photo_of_agreement=None,
            advance_payment=0,
            tp_of_pmt_id=1
        )
        session.add(new_report)
        await session.commit()
    await session.commit()
    return new_agreement


@router.get(
    "/get_list/",
    response_model=list[AgreementTutorResponse],
    status_code=status.HTTP_200_OK,
    description="Get list of agreements for tutor",
)
async def get_all_agreements_tutor(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[AgreementTutorResponse]:
    check_role_tutor(current_user)
    orders = await session.scalars(
        select(Agreement.order_number).where(Agreement.checked == False )
    )
    order = list(orders.all())
    data = []
    for o in order:
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
            .where(Order.order_number == o)
        )

        try:
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
                "order_number": agreement_data[0][0],
                "amount": agreement_data[0][1],
                "update_time": agreement_data[0][6],
                "agreement_details": {
                    "forks": forks,
                    "rejection": rejection
                }
            }
            data.append(agr_data)


        except:
            pass

    return data


@router.get(
    "engineer/get_list/",
    response_model=list[AgreementBaseResponse],
    status_code=status.HTTP_200_OK,
    description="Get list of tutors for currently SuperUsers.",
)
async def get_all_agreements(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> list[Agreement]:
    agreements = await session.scalars(
        select(Agreement)
    )
    return list(agreements.all())




@router.put(
    "/approve/{order_number}",
    status_code=status.HTTP_201_CREATED,
    description="approve agreement by tutor",
)
async def approve_agreement(
    order_number: int,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    check_role_tutor(current_user)
    agreement = await session.scalar(select(Agreement).where(Agreement.order_number == order_number))
    if not agreement:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THIS_ORDER_DO_NOT_HAS_AGREEMENT",
        )
    await session.execute(update(Agreement).where(Agreement.order_number == order_number).values(checked = True,))
    await session.execute(update(Order).where(Order.order_number == order_number).values(stage_of_order = 1, ))
    await session.commit()


@router.delete(
    "/delete/{order_number}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="delete agreement by tutor",
)
async def delete_agreement(
    order_number: int,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    check_role_tutor(current_user)
    agreement = await session.scalar(select(Agreement).where(Agreement.order_number == order_number))
    if not agreement:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="THIS_ORDER_DO_NOT_HAS_AGREEMENT",
        )
    agreement = await session.execute(select(Agreement.agreement_id).where(Agreement.order_number == order_number))
    a = agreement.all()[0]
    forks = await session.execute(select(Fork.fork_id).where(Fork.agreement_id == a[0]))
    f = forks.all()
    for fork in f:
        await session.execute(delete(Fork).where(Fork.fork_id == fork[0]))
    await session.execute(delete(Rejection).where(Rejection.agreement_id == a[0]))
    await session.execute(delete(Agreement).where(Agreement.agreement_id == a[0]))
    await session.commit()