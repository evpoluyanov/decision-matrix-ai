from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    projects: Mapped[list["Project"]] = relationship(
        back_populates="owner",
    )

class AIRequestLog(Base):
    __tablename__ = "ai_request_logs"

    __table_args__ = (
        Index(
            "ix_ai_request_logs_user_created_at",
            "user_id",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    project_id: Mapped[int] = mapped_column(
        nullable=False,
    )

    feature: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="started",
        nullable=False,
    )

    input_tokens: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    output_tokens: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    reasoning_tokens: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    total_tokens: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text(
            "CURRENT_TIMESTAMP"
        ),
        nullable=False,
    )

    completed_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

class AuthRateLimit(Base):
    """Shared counters; keys contain HMAC digests, never plaintext emails/IPs."""
    __tablename__ = "auth_rate_limits"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    attempts: Mapped[int] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class AIDailyBudget(Base):
    __tablename__ = "ai_daily_budgets"
    __table_args__ = (
        CheckConstraint("allocated_microrub >= 0", name="ck_ai_budget_nonnegative"),
    )

    day: Mapped[date] = mapped_column(Date, primary_key=True)
    allocated_microrub: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)


class AIProviderCall(Base):
    """Durable money ledger, retained even if the user/request log is deleted."""
    __tablename__ = "ai_provider_calls"
    __table_args__ = (
        CheckConstraint("charged_microrub >= 0", name="ck_ai_call_nonnegative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    request_log_id: Mapped[int | None] = mapped_column(
        ForeignKey("ai_request_logs.id", ondelete="SET NULL"), index=True,
    )
    budget_day: Mapped[date] = mapped_column(ForeignKey("ai_daily_budgets.day"), index=True)
    provider: Mapped[str] = mapped_column(String(30))
    model: Mapped[str] = mapped_column(String(100))
    input_rub_per_million: Mapped[Decimal] = mapped_column(Numeric(14, 6))
    output_rub_per_million: Mapped[Decimal] = mapped_column(Numeric(14, 6))
    input_token_bound: Mapped[int] = mapped_column()
    output_token_bound: Mapped[int] = mapped_column()
    reserved_microrub: Mapped[int] = mapped_column(BigInteger)
    charged_microrub: Mapped[int] = mapped_column(BigInteger)
    estimated_microrub: Mapped[int | None] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(20), default="reserved")
    input_tokens: Mapped[int | None] = mapped_column()
    output_tokens: Mapped[int | None] = mapped_column()
    reasoning_tokens: Mapped[int | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    owner: Mapped[User] = relationship(
        back_populates="projects",
    )

    alternatives: Mapped[list["Alternative"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )

    criteria: Mapped[list["Criterion"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )

    ai_analysis: Mapped["ProjectAIAnalysis | None"] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        uselist=False,
    )


class ProjectAIAnalysis(Base):
    __tablename__ = "project_ai_analyses"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    result_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    result_factors_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    result_strengths_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    result_weaknesses_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    result_competitor: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    result_caveat: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    result_preliminary: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    decision_risks_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    decision_risks_preliminary: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    project: Mapped[Project] = relationship(
        back_populates="ai_analysis",
    )

class Alternative(Base):
    __tablename__ = "alternatives"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    ai_suggested_name: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    ai_explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    scores: Mapped[list["Score"]] = relationship(
        back_populates="alternative",
        cascade="all, delete-orphan",
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
    )

    project: Mapped[Project] = relationship(
        back_populates="alternatives",
    )


class Criterion(Base):
    __tablename__ = "criteria"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    weight: Mapped[float] = mapped_column(
        default=0.0,
        nullable=False,
    )

    ai_suggested_name: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    ai_suggested_weight: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    ai_criterion_explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    ai_weight_explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    scores: Mapped[list["Score"]] = relationship(
        back_populates="criterion",
        cascade="all, delete-orphan",
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
    )

    project: Mapped[Project] = relationship(
        back_populates="criteria",
    )


class Score(Base):
    __tablename__ = "scores"

    __table_args__ = (
        UniqueConstraint(
            "alternative_id",
            "criterion_id",
            name="uq_score_alternative_criterion",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Сохранённое пользователем значение.
    # NULL означает, что пользователь ещё не подтвердил
    # оценку кнопкой «Сохранить матрицу».
    value: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    # Текущее независимое предложение ИИ.
    ai_value: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    ai_explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    alternative_id: Mapped[int] = mapped_column(
        ForeignKey("alternatives.id"),
        nullable=False,
    )

    criterion_id: Mapped[int] = mapped_column(
        ForeignKey("criteria.id"),
        nullable=False,
    )

    alternative: Mapped[Alternative] = relationship(
        back_populates="scores",
    )

    criterion: Mapped[Criterion] = relationship(
        back_populates="scores",
    )
