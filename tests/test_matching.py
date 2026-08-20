from types import SimpleNamespace

from app.models.subscriptions import Subscription
from app.services.matching import find_matches


async def test_returns_matching_subscription(db_session):
    subscription = Subscription(
        user_id=1,
        city="Poznan",
        price_max=3000,
        is_active=True,
    )
    db_session.add(subscription)
    await db_session.commit()
    apartment = SimpleNamespace(city="Poznan", price=3000, rooms=None, sq_meters=None, pets_allowed=None)
    matches = await find_matches(db_session, apartment)
    assert len(matches) == 1

async def test_excludes_wrong_city(db_session):
    subscription = Subscription(
        user_id=2,
        city="Poznan",
        price_max=2000,
        is_active=True,
    )
    db_session.add(subscription)
    await db_session.commit()
    apartment = SimpleNamespace(city="Warszawa", price=3000, rooms=None, sq_meters=None, pets_allowed=None)
    matches = await find_matches(db_session, apartment)
    assert len(matches) == 0

async def test_excludes_price_too_high(db_session):
    subscription = Subscription(
        user_id=1,
        city="Warszawa",
        price_max=2000,
        is_active=True,
    )
    db_session.add(subscription)
    await db_session.commit()
    apartment = SimpleNamespace(city = "Warszawa", price=5000, rooms=None, sq_meters=None, pets_allowed=None)
    matches = await find_matches(db_session, apartment)
    assert len(matches) == 0

async def test_not_active_subscription(db_session):
    subscription = Subscription(
        user_id=4,
        city="Warszawa",
        price_max=2000,
        is_active=False,
    )
    db_session.add(subscription)
    await db_session.commit()
    apartment = SimpleNamespace(city = "Warszawa", price=1500, rooms=None, sq_meters=None, pets_allowed=None)
    matches = await find_matches(db_session, apartment)
    assert len(matches) == 0

async def test_unknown_rooms_matches_only_flexible_subscription(db_session):
    subscription1 = Subscription(
        user_id=11,
        city="Warszawa",
        rooms_min=None,
        is_active=True,
    )
    subscription2 = Subscription(
        user_id=52,
        city="Warszawa",
        rooms_min=2,
        is_active=True,
    )
    db_session.add(subscription1)
    db_session.add(subscription2)
    await db_session.commit()
    apartment = SimpleNamespace(city = "Warszawa", price=5000, rooms=None, sq_meters=None, pets_allowed=None)
    matches = await find_matches(db_session, apartment)
    assert len(matches) == 1
    assert matches[0].id == subscription1.id