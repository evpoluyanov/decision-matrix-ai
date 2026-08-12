from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
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

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    projects: Mapped[list["Project"]] = relationship(
        back_populates="owner",
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
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


class Alternative(Base):
    __tablename__ = "alternatives"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
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

    value: Mapped[float] = mapped_column(
        nullable=False,
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