from sqlalchemy import select, or_

from app.models.subscriptions import Subscription
from app.models.users import User
from app.services.notifier import send_tg_message


async def find_matches(session,apartment):
    conditions = [
        Subscription.city == apartment.city,
        Subscription.is_active == True,
        or_(Subscription.price_min.is_(None), Subscription.price_min <= apartment.price),
        or_(Subscription.price_max.is_(None), Subscription.price_max >= apartment.price),
        or_(Subscription.pets_allowed.is_(None), Subscription.pets_allowed == apartment.pets_allowed),
    ]
    if apartment.rooms is not None:
        conditions.append(or_(Subscription.rooms_min.is_(None), Subscription.rooms_min <= apartment.rooms))
        conditions.append(or_(Subscription.rooms_max.is_(None), Subscription.rooms_max >= apartment.rooms))
    else:
        conditions.append(Subscription.rooms_min.is_(None))
        conditions.append(Subscription.rooms_max.is_(None))
    if apartment.sq_meters is not None:
        conditions.append(or_(Subscription.sq_meters_min.is_(None), Subscription.sq_meters_min <= apartment.sq_meters))
        conditions.append(or_(Subscription.sq_meters_max.is_(None), Subscription.sq_meters_max >= apartment.sq_meters))
    else:
        conditions.append(Subscription.sq_meters_min.is_(None))
        conditions.append(Subscription.sq_meters_max.is_(None))

    stmt = select(Subscription).where(*conditions)
    result = await session.execute(stmt)
    return result.scalars().all()

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


