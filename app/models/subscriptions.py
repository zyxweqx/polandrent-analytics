from sqlalchemy import String, Float, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped,mapped_column

from app.models.base import Base

class Subscriptions(Base):
    __tablename__ = 'subscriptions'

    id = Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))

    city: Mapped[str] = mapped_column(String(100))
    district: Mapped[str | None] = mapped_column(String(100))

    price_min: Mapped[float | None] = mapped_column(Float)
    price_max: Mapped[float | None] = mapped_column(Float)

    rooms_min: Mapped[float | None] = mapped_column(Integer)
    rooms_max: Mapped[float | None] = mapped_column(Integer)
    sq_meters_min: Mapped[float | None] = mapped_column(Float)
    sq_meters_max: Mapped[float | None] = mapped_column(Float)

    pets_allowed: Mapped[bool | None] = mapped_column(Boolean)

    is_owner: Mapped[bool | None] = mapped_column(Boolean)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, city={self.city}, max_price={self.price_max})>"
