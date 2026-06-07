import asyncio

from app.core.database import async_session_maker
from app.models.apartments import Apartment


async def add_test_apartment():
    print("Creating test apartment")

    new_apartment = Apartment(
        url="https://www.olx.pl/nieruchomosci/mieszkania/wynajem/poznan/",
        title="Przytulna kawalerka w centrum",
        city="Poznan",
        district="Stare Miasto",
        price=2200.0,
        additional_rent=400,
        sq_meters=32.5,
        rooms=1,
        floor=3,
        is_furnished=True,
        pets_allowed=False
    )

    async with async_session_maker() as session:

        session.add(new_apartment)

        await session.commit()

    print("Successfully created test apartment")

if __name__ == "__main__":
    asyncio.run(add_test_apartment())