from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
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