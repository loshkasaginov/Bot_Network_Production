# SQL Alchemy models declaration.
# https://docs.sqlalchemy.org/en/20/orm/quickstart.html#declare-models
# mapped_column syntax from SQLAlchemy 2.0.

# https://alembic.sqlalchemy.org/en/latest/tutorial.html
# Note, it is used by alembic migrations logic, see `alembic/env.py`

# Alembic shortcuts:
# # create migration
# alembic revision --autogenerate -m "migration_name"

# # apply all migrations
# alembic upgrade head


import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(Base):
    __tablename__ = "user_account"

    user_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), primary_key=True, default=lambda _: str(uuid.uuid4())
    )
    role: Mapped[str] = mapped_column(String(256), nullable=False, default="Engineer")
    user_name: Mapped[str] = mapped_column(
        String(256), nullable=False, unique=True, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    refresh_token: Mapped[str] = mapped_column(
        String(512), nullable=False, unique=True, index=True
    )
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    exp: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("user_account.user_id", ondelete="CASCADE"),
    )
    user: Mapped["User"] = relationship(back_populates="refresh_tokens")



class Order(Base):
    __tablename__ = "order"

    order_number: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    tutors_number: Mapped[int] = mapped_column(ForeignKey("tutor.tutors_number"), nullable=True)
    engineers_number: Mapped[int] = mapped_column(ForeignKey("engineer.engineers_number"), nullable=True)
    stage_of_order: Mapped[int] = mapped_column(BigInteger, nullable=True, default=0)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=True)
    done: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    tutor: Mapped["Tutor"] = relationship("Tutor", back_populates="orders", uselist=False)
    engineer: Mapped["Engineer"] = relationship("Engineer", back_populates="orders", uselist=False)
    agreement: Mapped["Agreement"] = relationship("Agreement", back_populates="order", uselist=False)
    prepayment: Mapped["Prepayment"] = relationship("Prepayment", back_populates="order", uselist=False)
    outlays: Mapped[list["OutlayRecord"]] = relationship("OutlayRecord", back_populates="order")
    report: Mapped["Report"] = relationship("Report", back_populates="order", uselist=False)
    stationary: Mapped["Stationary"] = relationship("Stationary", back_populates="order", uselist=False)



class Tutor(Base):
    __tablename__ = 'tutor'
    tutors_number: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("user_account.user_id", ondelete="CASCADE"), nullable = True
    )
    link: Mapped[str] = mapped_column(String, autoincrement=False, nullable = True)
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="tutor")
    name: Mapped[str] = mapped_column(String, autoincrement=False, nullable = False, unique=True)


class Engineer(Base):
    __tablename__ = 'engineer'
    engineers_number: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("user_account.user_id", ondelete="CASCADE"), nullable = True
    )
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="engineer")
    penalties: Mapped[list["Penalty"]] = relationship("Penalty", back_populates="engineer")
    link: Mapped[str] = mapped_column(String, autoincrement=False, nullable = True)
    name: Mapped[str] = mapped_column(String, autoincrement=False, nullable = False)


class StateEngineer(Base):
    __tablename__ = 'state_engineer'
    state_engineers_number: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("user_account.user_id", ondelete="CASCADE"), nullable = True
    )
    # orders: Mapped[list["Order"]] = relationship("Order", back_populates="state_engineer")
    link: Mapped[str] = mapped_column(String, autoincrement=False, nullable = True)
    name: Mapped[str] = mapped_column(String, autoincrement=False, nullable = False)
    stationaries: Mapped[list["Stationary"]] = relationship("Stationary", back_populates="state_engineer")


class Agreement(Base):
    __tablename__ = 'agreement'
    agreement_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=True)
    checked:Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    order_number: Mapped[int] = mapped_column(ForeignKey("order.order_number"), nullable=False, unique=True)
    order: Mapped["Order"] = relationship("Order", back_populates="agreement")
    forks: Mapped[list["Fork"]] = relationship("Fork", back_populates="agreement")
    rejection: Mapped["Rejection"] = relationship("Rejection", back_populates="agreement", uselist=False)

class Fork(Base):
    __tablename__ = 'fork'

    fork_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    agreement_id: Mapped[int] = mapped_column(ForeignKey("agreement.agreement_id"), nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=True)
    description: Mapped[str] = mapped_column(String, autoincrement=False, nullable = False)
    agreement: Mapped["Agreement"] = relationship("Agreement", back_populates="forks")


class Rejection(Base):
    __tablename__ = 'rejection'

    rejection_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    agreement_id: Mapped[int] = mapped_column(ForeignKey("agreement.agreement_id"), nullable=False, unique=True)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=True)
    description: Mapped[str] = mapped_column(String, autoincrement=False, nullable=False)
    agreement: Mapped["Agreement"] = relationship("Agreement", back_populates="rejection")


class Prepayment(Base):
    __tablename__ = 'prepayment'
    prepayment_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_number: Mapped[int] = mapped_column(ForeignKey("order.order_number"), nullable=False, unique=True)
    checked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=True)
    tp_of_pmt_id: Mapped[int] = mapped_column(ForeignKey("type_of_payment.tp_of_pmt_id"), nullable=False)
    order: Mapped["Order"] = relationship("Order", back_populates="prepayment")
    type_of_payment: Mapped["TypeOfPayment"] = relationship("TypeOfPayment", back_populates="prepayments", uselist=False)


class TypeOfPayment(Base):
    __tablename__ = 'type_of_payment'
    tp_of_pmt_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    type_of_payment: Mapped[str] = mapped_column(String, autoincrement=False, nullable=False)
    prepayments: Mapped[list["Prepayment"]] = relationship("Prepayment", back_populates="type_of_payment")
    outlays: Mapped[list["OutlayRecord"]] = relationship("OutlayRecord", back_populates="type_of_payment")
    reports: Mapped[list["Report"]] = relationship("Report", back_populates="type_of_payment")

class OutlayRecord(Base):
    __tablename__ = 'outlay_record'
    outlay_record_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, autoincrement=False, nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=True)
    checked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    cheque: Mapped[str] = mapped_column(String, autoincrement=False, nullable=False)
    order_number: Mapped[int] = mapped_column(ForeignKey("order.order_number"), nullable=False)
    tp_of_pmt_id: Mapped[int] = mapped_column(ForeignKey("type_of_payment.tp_of_pmt_id"), nullable=False)
    order: Mapped["Order"] = relationship("Order", back_populates="outlays")
    type_of_payment: Mapped["TypeOfPayment"] = relationship("TypeOfPayment", back_populates="outlays", uselist=False)

class Report(Base):
    __tablename__ = 'report'
    report_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_number: Mapped[int] = mapped_column(ForeignKey("order.order_number"), nullable=False)
    all_amount: Mapped[int] = mapped_column(BigInteger, nullable=True)
    checked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    clear_amount: Mapped[int] = mapped_column(BigInteger, nullable=True)
    photo_of_agreement: Mapped[str] = mapped_column(String, autoincrement=False, nullable=True)
    advance_payment: Mapped[int] = mapped_column(BigInteger, nullable=True, default=0)
    tp_of_pmt_id: Mapped[int] = mapped_column(ForeignKey("type_of_payment.tp_of_pmt_id"), nullable=False)
    order: Mapped["Order"] = relationship("Order", back_populates="report")
    type_of_payment: Mapped["TypeOfPayment"] = relationship("TypeOfPayment", back_populates="reports", uselist=False)


class Stationary(Base):
    __tablename__ = 'stationary'
    stationary_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_number: Mapped[int] = mapped_column(ForeignKey("order.order_number"), nullable=False)
    state_engineers_number: Mapped[int] = mapped_column(ForeignKey("state_engineer.state_engineers_number"), nullable=True)
    priority: Mapped[int] = mapped_column(BigInteger, nullable=True, default=1)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=True)
    photo: Mapped[str] = mapped_column(String, autoincrement=False, nullable=False)
    description: Mapped[str] = mapped_column(String, autoincrement=False, nullable=False)
    done: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    order: Mapped["Order"] = relationship("Order", back_populates="stationary", uselist=False)
    state_engineer: Mapped["StateEngineer"] = relationship("StateEngineer", back_populates="stationaries", uselist=False)


class Penalty(Base):
    __tablename__ = 'penalty'
    penalty_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    engineers_number: Mapped[int] = mapped_column(ForeignKey("engineer.engineers_number"),nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=True)
    description: Mapped[str] = mapped_column(String, autoincrement=False, nullable=False)
    engineer: Mapped["Engineer"] = relationship("Engineer", back_populates="penalties")