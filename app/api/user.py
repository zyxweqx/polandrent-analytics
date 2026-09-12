from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.models.users import User
from app.schemas.users import UserCreate

router = APIRouter(prefix="/user", tags=["Users"], dependencies=[Depends(verify_api_key)])

@router.post("/")
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    new_user = User(**user_in.model_dump())

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.get("/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.id == user_id)

    result = await db.execute(query)

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user