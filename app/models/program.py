from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Program(Base):
    __tablename__ = "programs"

    program_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    min_age: Mapped[int] = mapped_column(Integer, nullable=False)
    max_age: Mapped[int] = mapped_column(Integer, nullable=False)