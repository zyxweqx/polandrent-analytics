from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.models.apartments import Apartment
from app.schemas.apartments import (
    ApartmentsCreate,
    ApartmentsResponse,
    ApartmentsUpdate,
)
from app.services.matching import find_matches, notify_matched_users

router = APIRouter(prefix="/apartments", tags=["apartments"],dependencies=[Depends(verify_api_key)])

@router.get("/{aps_id}", response_model=ApartmentsResponse)
async def get_apartment(aps_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Apartment).where(Apartment.id == aps_id)
    result = await db.execute(query)
    aps = result.scalar_one_or_none()

    if not aps:
        raise HTTPException(status_code=404, detail="Apartment not found")
    return aps

@router.get("/", response_model=list[ApartmentsResponse])
async def get_all_apartments(db: AsyncSession = Depends(get_db)):
    query = select(Apartment).order_by(Apartment.id)
    result = await db.execute(query)
    aps = result.scalars().all()
    return aps

@router.post("/", response_model=ApartmentsResponse)
async def create_apartment(aps_data: ApartmentsCreate, db: AsyncSession = Depends(get_db)):
    new_ap = Apartment(**aps_data.model_dump())
    db.add(new_ap)

    try:
        await db.commit()
        await db.refresh(new_ap)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Apartment already exists")
    matches = await find_matches(db,new_ap)
    await notify_matched_users(db, matches, new_ap)

    return new_ap

@router.patch("/{aps_id}", response_model=ApartmentsResponse)
async def update_apartment(aps_id: int, aps_data: ApartmentsUpdate, db: AsyncSession = Depends(get_db)):
    query = select(Apartment).where(Apartment.id == aps_id)
    result = await db.execute(query)
    aps = result.scalar_one_or_none()
    if not aps:
        raise HTTPException(status_code=404, detail="Apartment not found")

    updated_data = aps_data.model_dump(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(aps, key, value)

    db.add(aps)
    await db.commit()
    await db.refresh(aps)
    return aps

@router.delete("/{aps_id}")
async def delete_apartment(aps_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Apartment).where(Apartment.id == aps_id)
    result = await db.execute(query)
    aps = result.scalar_one_or_none()

    if not aps:
        raise HTTPException(status_code=404, detail="Apartment not found")
    await db.delete(aps)
    await db.commit()

    return {"detail": f"Apartment {aps_id} successfully deleted!"}

