from datetime import datetime, timezone

from sqlalchemy import String, BIGINT, BOOLEAN, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BIGINT, unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)

    sessions: Mapped[list["UserSession"]] = relationship("UserSession", back_populates="user", cascade="all, delete")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user_agent: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(tz=timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(default=datetime.now(tz=timezone.utc))
    is_active: Mapped[bool] = mapped_column(default=True)

    user: Mapped["User"] = relationship("User", back_populates="sessions", lazy="joined")