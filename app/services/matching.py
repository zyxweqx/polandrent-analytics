import logging

from sqlalchemy import or_, select

from app.models.subscriptions import Subscription
from app.models.users import User
from app.services.notifier import send_tg_message

logger = logging.getLogger(__name__)


async def find_matches(session,apartment):
    conditions = [
        Subscription.city == apartment.city,
        Subscription.is_active,
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

async def build_notifications(session, matches, apartment):
    notifications = []
    user_ids = [subscription.user_id for subscription in matches]
    user_query = select(User).where(User.id.in_(user_ids))
    user_result = await session.execute(user_query)
    users_by_id = {user.id: user for user in user_result.scalars().all()}
    for subscription in matches:
        user = users_by_id.get(subscription.user_id)
        if not user:
            continue
        text = (
            f"🏢 <b>{apartment.title}</b>\n"
            f"📍 City: {apartment.city}\n"
            f"💰 Price: {apartment.price:.0f} zł\n"
            f"🔗 <a href='{apartment.url}'>Open listing</a>"
        )
        notifications.append((user.telegram_id, text))
    return notifications

async def send_notifications(notifications):
    for telegram_id, text in notifications:
        try:
            await send_tg_message(telegram_id, text)
        except Exception:
            logger.exception("Failed to notify user %s", telegram_id)
