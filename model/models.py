from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)

    bank_accounts: Mapped[list["BankAccount"]] = relationship(back_populates="user")
    budgets: Mapped[list["Budget"]] = relationship(back_populates="user")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    account_name: Mapped[str | None] = mapped_column(String(255))
    iban: Mapped[str | None] = mapped_column(String(50))
    account_type: Mapped[str | None] = mapped_column(String(50))
    balance: Mapped[float] = mapped_column(Numeric(15, 2), default=0.00)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)

    user: Mapped["User"] = relationship(back_populates="bank_accounts")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="account")


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str | None] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="merchant")
    recurring_rules: Mapped[list["RecurringRule"]] = relationship(back_populates="merchant")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    parent_id: Mapped[UUID | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))

    icon: Mapped[str | None] = mapped_column(String(100))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)

    parent: Mapped[Optional["Category"]] = relationship(remote_side=[id])


class CategoryRule(Base):
    __tablename__ = "category_rules"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    merchant_pattern: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)

    category: Mapped["Category"] = relationship()


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (Index("idx_transactions_account_date", "account_id", "transaction_date"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    account_id: Mapped[UUID] = mapped_column(ForeignKey("bank_accounts.id", ondelete="CASCADE"))

    merchant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("merchants.id", ondelete="SET NULL")
    )

    category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL")
    )

    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    booking_date: Mapped[date | None] = mapped_column(Date)

    description: Mapped[str | None] = mapped_column(Text)
    import_hash: Mapped[str | None] = mapped_column(String(64), unique=True)
    is_pending: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    account: Mapped["BankAccount"] = relationship(back_populates="transactions")
    merchant: Mapped[Optional["Merchant"]] = relationship(back_populates="transactions")
    category: Mapped[Optional["Category"]] = relationship()
    tags: Mapped[list["Tag"]] = relationship(secondary="transaction_tags", lazy="selectin")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)


transaction_tags = Table(
    "transaction_tags",
    Base.metadata,
    Column(
        "transaction_id",
        PG_UUID(as_uuid=True),
        ForeignKey("transactions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id", PG_UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    ),
)


class Budget(Base):
    __tablename__ = "budgets"

    __table_args__ = (CheckConstraint("period_type IN ('monthly','quarterly','yearly')"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))

    period_type: Mapped[str] = mapped_column(String(20))
    amount_limit: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)

    user: Mapped["User"] = relationship(back_populates="budgets")


class RecurringRule(Base):
    __tablename__ = "recurring_rules"

    __table_args__ = (CheckConstraint("frequency IN ('monthly','yearly')"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    merchant_id: Mapped[UUID] = mapped_column(ForeignKey("merchants.id", ondelete="CASCADE"))

    expected_amount: Mapped[float | None] = mapped_column(Numeric(15, 2))
    frequency: Mapped[str] = mapped_column(String(20))
    last_detected: Mapped[date | None] = mapped_column(Date)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)

    merchant: Mapped["Merchant"] = relationship(back_populates="recurring_rules")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    __table_args__ = (Index("idx_prt_token_hash", "token_hash"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship()


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_entity", "entity_type", "entity_id"),
        Index("idx_audit_user", "user_id"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)

    old_values: Mapped[dict | None] = mapped_column(JSONB)
    new_values: Mapped[dict | None] = mapped_column(JSONB)

    ip_address: Mapped[str | None] = mapped_column(String(50))
    user_agent: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[Optional["User"]] = relationship(back_populates="audit_logs")
