
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.models.subscriptions import Subscription
from app.models.users import User
from app.schemas.subscriptions import (
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionUpdate,
)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"], dependencies=[Depends(verify_api_key)])

@router.post("/", response_model=SubscriptionResponse)
async def create_subscription(sub_in: SubscriptionCreate, db: AsyncSession = Depends(get_db)):
    user_query = select(User).where(User.id == sub_in.user_id)
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_sub = Subscription(**sub_in.model_dump())
    db.add(new_sub)
    await db.commit()
    await db.refresh(new_sub)

    return new_sub

@router.get("/user/{user_id}", response_model=list[SubscriptionResponse])
async def get_user_subscriptions(user_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Subscription).where(Subscription.user_id == user_id)
    result = await db.execute(query)

    subscriptions = result.scalars().all()

    return subscriptions

@router.patch("/{sub_id}", response_model=SubscriptionResponse)
async def update_subscription(sub_id: int, sub_in: SubscriptionUpdate, db: AsyncSession = Depends(get_db)):
    query = select(Subscription).where(Subscription.id == sub_id)
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    update_data = sub_in.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(subscription, key, value)
    await db.commit()
    await db.refresh(subscription)

    return subscription

@router.delete("/{sub_id}")
async def delete_subscription(sub_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Subscription).where(Subscription.id == sub_id)
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    await db.delete(subscription)
    await db.commit()

    return {"detail": f"Subscription {sub_id} successfully deleted!"}




