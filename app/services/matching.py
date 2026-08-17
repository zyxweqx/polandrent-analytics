from sqlalchemy import select, or_

from app.models.subscriptions import Subscription
from app.models.users import User
from app.services.notifier import send_tg_message


async def find_matches(session,apartment):
    stmt = select(Subscription).where(
        Subscription.city == apartment.city,
        Subscription.is_active == True,
        or_(
            Subscription.price_min.is_(None),
            Subscription.price_min <= apartment.price,
        ),
        or_(
            Subscription.price_max.is_(None),
            Subscription.price_max >= apartment.price,
        ),
        or_(
            Subscription.rooms_min.is_(None),
            Subscription.rooms_min <= apartment.rooms,
        ),
        or_(
            Subscription.rooms_max.is_(None),
            Subscription.rooms_max >= apartment.rooms,
        ),
        or_(
            Subscription.sq_meters_min.is_(None),
            Subscription.sq_meters_min <= apartment.sq_meters,
        ),
        or_(
            Subscription.sq_meters_max.is_(None),
            Subscription.sq_meters_max >= apartment.sq_meters,
        ),
        or_(
            Subscription.pets_allowed.is_(None),
            Subscription.pets_allowed == apartment.pets_allowed,
        ),
    )
    result = await session.execute(stmt)
    matches = result.scalars().all()
    return matches

async def notify_matched_users(session, matches, apartment):
    for subscription in matches:
        user_query = select(User).where(User.id == subscription.user_id)
        user_result = await session.execute(user_query)
        user = user_result.scalars().one_or_none()
        if not user:
            continue
        text = (
            f"🏢 <b>{apartment.title}</b>\n"
            f"📍 City: {apartment.city}\n"
            f"💰 Price: {apartment.price:.0f} zł\n"
            f"🔗 <a href='{apartment.url}'>Open listing</a>"
        )
        await send_tg_message(user.telegram_id, text)


