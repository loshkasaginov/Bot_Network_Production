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
    role: Mapped[int] = mapped_column(String(256), nullable=False, default="engineer")
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
    state_engineers_number: Mapped[int] = mapped_column(ForeignKey("state_engineer.state_engineers_number"), nullable=True)
    # engineers_number: Mapped[int] = mapped_column(ForeignKey("engineer.engineers_number"), nullable=True)
    # prepayment_id: Mapped[int] = mapped_column(ForeignKey("prepayment.prepayment_id"), nullable=True)
    # agreement_id: Mapped[int] = mapped_column(ForeignKey("agreement.agreement_id"), nullable=True)
    # registration_id: Mapped[int] = mapped_column(ForeignKey("registration.registration_id"), nullable=True)
    # report_id: Mapped[int] = mapped_column(ForeignKey("report.report_id"), nullable=True)
    # stationary_id: Mapped[int] = mapped_column(ForeignKey("stationary.stationary_id"), nullable=True)
    stage_of_order: Mapped[int] = mapped_column(BigInteger, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=True)
    model: Mapped[str] = mapped_column(String, nullable=True)
    done: Mapped[bool] = mapped_column(Boolean, nullable=True)
    tutor: Mapped["Tutor"] = relationship("Tutor", back_populates="orders")
    engineer: Mapped["Engineer"] = relationship("Engineer", back_populates="orders")
    state_engineer: Mapped["StateEngineer"] = relationship("StateEngineer", back_populates="orders")
    # prepayment: Mapped["Prepayment"] = relationship("Prepayment", back_populates="orders")
    # agreement: Mapped["Agreement"] = relationship("Agreement", back_populates="orders")
    # registration: Mapped["Registration"] = relationship("Registration", back_populates="orders")
    # report: Mapped["Report"] = relationship("Report", back_populates="orders")
    # stationary: Mapped["Stationary"] = relationship("Stationary", back_populates="orders")

# Remember to define the back_populates on the related models as well for bidirectional relationship


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
    link: Mapped[str] = mapped_column(String, autoincrement=False, nullable = True)
    name: Mapped[str] = mapped_column(String, autoincrement=False, nullable = False)


class StateEngineer(Base):
    __tablename__ = 'state_engineer'
    state_engineers_number: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("user_account.user_id", ondelete="CASCADE"), nullable = True
    )
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="state_engineer")
    link: Mapped[str] = mapped_column(String, autoincrement=False, nullable = True)
    name: Mapped[str] = mapped_column(String, autoincrement=False, nullable = False)