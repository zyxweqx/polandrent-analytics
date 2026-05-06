import datetime
from typing import Optional

from sqlalchemy import String, Float, Integer, Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped,mapped_column


class Base(DeclarativeBase):
    pass

class Apartment(Base):
    __tablename__ = 'apartments'

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100))
    district: Mapped[str | None] = mapped_column(String(100))

    price: Mapped[float] = mapped_column(Float)
    additional_rent: Mapped[float | None] = mapped_column(Float)
    sq_meters: Mapped[float | None] = mapped_column(Float)
    rooms: Mapped[int | None] = mapped_column(Integer)
    floor: Mapped[int | None] = mapped_column(Integer)

    is_furnished: Mapped[bool | None] = mapped_column(Boolean)
    pets_allowed: Mapped[bool | None] = mapped_column(Boolean)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Apartment(id={self.id}, city={self.city}, price={self.price})>"