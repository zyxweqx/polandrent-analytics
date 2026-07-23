from sqlalchemy import select, or_

from app.models.subscriptions import Subscription

async def find_matches(session,apartment):
    stmt = select(Subscription).where(
        Subscription.city == apartment.city,

        or_(
            Subscription.price_min.is_(None),
            Subscription.price_min <= apartment.price,
        ),
        or_(
            Subscription.price_max.is_(None),
            Subscription.price_max  >= apartment.price,
        ),
    )
    result = await session.execute(stmt)
    matches = result.scalars().all()
    return matches

