import asyncio
import re
from typing import List, Dict, Any, Optional, Tuple

from playwright.async_api import async_playwright, Page
from app.core.database import async_session_maker
from app.models.apartments import Apartment, Base
from sqlalchemy import select
from app.core.database import engine

def clean_price_text(raw_price: str) -> float:
        clean_price = raw_price.replace(" ", "").replace("zł", "").replace("donegocjacji", "").replace("\n","").replace(",", ".")
        final_price = float(clean_price)
        return final_price

async def dismiss_popups(page) -> None:
    print("Dismissing popups...")
    await page.keyboard.press("Escape")
    await page.wait_for_timeout(1000)
    survey_frame = page.frame_locator("[id*='contextual-widget-host']")
    dismiss_btn = survey_frame.get_by_role("button", name="Dismiss study invitation")

    try:
        await dismiss_btn.wait_for(state="visible", timeout=5000)
        print("Survey popup detected, clicking dismiss...")
        await dismiss_btn.click()
    except Exception:
        print("Survey popup did not appear this time.")

    accept_cookies_btn = page.get_by_role("button", name="Akceptuj wszystkie")
    try:
        if await accept_cookies_btn.is_visible():
            print("Cookie banner detected, accepting...")
            await accept_cookies_btn.click()
    except Exception:
        print("Cookie button not clickable or missing.")

    await page.locator('[data-cy="l-card"]').first.wait_for(state="visible")

async def dismiss_otodom_cookies(page) -> None:
    try:
        otodom_cookies_btn = page.get_by_role("button", name="Akceptuj wszystkie")

        if await otodom_cookies_btn.is_visible(timeout=2000):
            await otodom_cookies_btn.click()
            await page.wait_for_timeout(500)
    except Exception:
        print("Cookie button not clickable or missing.")

async def parse_apartments_list(page: Page) -> List[Dict[str, Any]]:
    print("Parsing apartments list...")
    await page.locator('[data-cy="l-card"]').first.wait_for(state="visible")
    all_cards = await page.locator('[data-cy="l-card"]').all()
    print(f"Listings found on the page: {len(all_cards)}")

    results: List[Dict[str, Any]] = []

    for i, card in enumerate(all_cards):
        try:
            title_text = await card.locator('[data-testid="ad-card-title"] h4').inner_text(timeout=1000)

            link_element = card.locator('a').first
            raw_url = await link_element.get_attribute("href")
            url = "https://www.olx.pl" + raw_url if raw_url.startswith("/d/") else raw_url

            raw_price = await card.locator('[data-testid="ad-price"]').first.inner_text(timeout=1000)
            final_price = clean_price_text(raw_price)

            print(f"Parsed: {title_text} | Price: {final_price}")

            results.append({
                "title": title_text,
                "price": final_price,
                "url": url,
                "city": "Poznan"
            })
        except Exception:
            continue

    return results

async def save_to_db(apartments_data: List[Dict[str, Any]]) -> None:
    async with async_session_maker() as session:
        added_count = 0
        skipped_count = 0

        for apt_data in apartments_data:
            stmt = select(Apartment).where(Apartment.url == apt_data["url"])
            result = await session.execute(stmt)
            existing_apt = result.scalar_one_or_none()

            if existing_apt:
                skipped_count += 1
                continue

            new_apt = Apartment(
                url=apt_data["url"],
                title=apt_data["title"],
                price=apt_data["price"],
                city=apt_data["city"],
                sq_meters=apt_data.get("sq_meters"),
                rooms=apt_data.get("rooms"),
                floor=apt_data.get("floor"),
                additional_rent=apt_data.get("additional_rent"),
                district=apt_data.get("district")
            )
            session.add(new_apt)
            added_count += 1
        print(f"Committing to the database... (Added: {added_count}, Skipped: {skipped_count})")
        await session.commit()

async def parse_olx_details(page: Page) -> Tuple[Optional[float], Optional[int], Optional[int], Optional[float], Optional[str]]:
    sq_meters, rooms, floor,additional_rent,district = None, None, None, None, None

    try:
        area_element = page.locator("p").filter(has_text="Powierzchnia:").first
        await area_element.wait_for(state="visible", timeout=3000)
        area_text = await area_element.inner_text()
        match = re.search(r'\d+[.,]?\d*', area_text)
        if match:
            clean_area = match.group().replace(",", ".")
            sq_meters = float(clean_area)
    except Exception as e:
         print(f"Not found meters on this page {e}")

    try:
        rooms_element = page.locator("p").filter(has_text="Liczba pokoi:").first
        await rooms_element.wait_for(state="visible", timeout=3000)
        rooms_text = await rooms_element.inner_text()
        if "Kawalerka" in rooms_text or "kawalerka" in rooms_text:
             rooms = 1
        else:
             match = re.search(r'\d+', rooms_text)
             if match:
                  rooms = int(match.group())
    except Exception:
        print("Not found rooms on this page")

    try:
        floor_element = page.locator("p").filter(has_text="Poziom:").first
        await floor_element.wait_for(state="visible", timeout=3000)
        floor_text = await floor_element.inner_text()
        text_lower = floor_text.lower()
        if "parter" in text_lower:
            floor = 0
        elif "suteryna" in text_lower:
            floor = -1
        elif "poddasze" in text_lower:
            floor = 99
        else:
            match = re.search(r'\d+', floor_text)
            if match:
                floor = int(match.group())
    except Exception:
          print("Not found floors on this page")

    try:
        rent_element = page.locator("p").filter(has_text="Czynsz").first
        await rent_element.wait_for(state="visible", timeout=2000)
        rent_text = await rent_element.inner_text()
        clean_rent_text = rent_text.replace(" ", "").replace(" ", "")
        match = re.search(r'\d+[.,]?\d*', clean_rent_text)
        if match: additional_rent = float(match.group().replace(",", "."))
    except Exception:
        print ("Not found rent on this page")

    try:
        loc_element = page.locator("p").filter(has_text="Poznań").first
        await loc_element.wait_for(state="visible", timeout=2000)
        loc_text = await loc_element.inner_text()
        if "," in loc_text:
            parts = loc_text.split(",")
            if len(parts) > 1:
                district = parts[1].strip()
    except Exception:
        print("Not found district on this page")

    return sq_meters, rooms, floor, additional_rent, district

async def parse_otodom_details(page: Page) -> Tuple[Optional[float], Optional[int], Optional[int], Optional[float], Optional[str]]:
    await dismiss_otodom_cookies(page)
    sq_meters, rooms, floor,additional_rent, district = None, None, None, None, None

    try:
        area_element = page.locator('div:has-text("Powierzchnia") + div').first
        await area_element.wait_for(state="visible", timeout=3000)
        area_text = await area_element.inner_text()
        match = re.search(r'\d+[.,]?\d*', area_text)
        if match:
            sq_meters = float(match.group().replace(",", "."))
    except Exception as e:
        print(f"Not found area on this page {e}")

    try:
        rooms_element = page.locator('div:has-text("Liczba pokoi") + div').first
        await rooms_element.wait_for(state="visible", timeout=3000)
        rooms_text = await rooms_element.inner_text()
        if "Kawalerka" in rooms_text or "kawalerka" in rooms_text:
            rooms = 1
        else:
            match = re.search(r'\d+', rooms_text)
            if match:
                rooms = int(match.group())
    except Exception as e:
        print(f"Not found rooms on this page {e}")

    try:
        floor_element = page.locator('div:has-text("Piętro") + div').first
        await floor_element.wait_for(state="visible", timeout=3000)
        floor_text = await floor_element.inner_text()
        text_lower = floor_text.lower()
        if "parter" in text_lower:
            floor = 0
        elif "suteryna" in text_lower:
            floor = -1
        elif "poddasze" in text_lower:
            floor = 99
        else:
            match = re.search(r'\d+', floor_text)
            if match:
                floor = int(match.group())
    except Exception as e:
        print(f"Not found floors on this page {e}")

    try:
        rent_element = page.locator('div:has-text("Czynsz") + div').first
        await rent_element.wait_for(state="visible", timeout=2000)
        rent_text = await rent_element.inner_text()
        clean_rent_text = rent_text.replace(" ", "").replace(" ", "")
        match = re.search(r'\d+[.,]?\d*', clean_rent_text)
        if match: additional_rent = float(match.group().replace(",", "."))
    except Exception:
        print("Not found rent on this page")

    try:
        loc_element = page.locator('a[href*="#map"]').first
        await loc_element.wait_for(state="visible", timeout=2000)
        loc_text = await loc_element.inner_text()

        if "Poznań" in loc_text:
            parts = loc_text.split(",")
            district = parts[-1].strip()
    except Exception:
        print("Not found district on this page")

    return sq_meters, rooms, floor, additional_rent, district

async def get_apartment_details(page: Page, url: str) -> Dict[str, Any]:
    print(f"[Details] Entry inside: {url}")
    try:
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(1500)

        sq_meters, rooms, floor, additional_rent, district = None, None, None, None, None

        if "olx.pl" in url:
            sq_meters, rooms, floor,additional_rent, district = await parse_olx_details(page)
        elif "otodom.pl" in url:
            sq_meters, rooms, floor,additional_rent, district = await parse_otodom_details(page)

        print(f" -> Area: {sq_meters} m2 | Rooms: {rooms} | Floor: {floor}")

        return {
            "sq_meters": float(sq_meters) if sq_meters is not None else None,
            "rooms": int(rooms) if rooms is not None else None,
            "floor": int(floor) if floor is not None else None,
            "additional_rent": float(additional_rent) if additional_rent is not None else None,
            "district": district if district is not None else None
        }

    except Exception as e:
        print(f"Error:{url}: {e}")
        return {"sq_meters": None, "rooms": None, "floor": None}

async def run_scraper() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            permissions=[]
        )

        page = await context.new_page()
        second_page = await context.new_page()

        MAX_PAGES = 50
        all_apartments_data = []

        for current_page in range(1, MAX_PAGES + 1):
            print(f"Scraping page {current_page} from {MAX_PAGES} pages")

            if current_page == 1:
                url = "https://www.olx.pl/nieruchomosci/mieszkania/wynajem/poznan/"
            else:
                url = f"https://www.olx.pl/nieruchomosci/mieszkania/wynajem/poznan/?page={current_page}"

            await page.goto(url, wait_until="domcontentloaded")

            if current_page == 1:
                await dismiss_popups(page)

            page_data = await parse_apartments_list(page)
            print("\n Apartments data:")

            for apt in page_data:
                details = await get_apartment_details(second_page, apt["url"])
                apt.update(details)

            await save_to_db(page_data)

            all_apartments_data.extend(page_data)

        await second_page.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
