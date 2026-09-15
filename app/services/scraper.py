import asyncio
import random
import re
from dataclasses import dataclass

import httpx
from playwright.async_api import Page, async_playwright
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

API_URL = "http://web:8000/apartments/"

CITY_DISPLAY_NAMES = {
    "poznan": "Poznań",
    "warszawa": "Warszawa",
    "krakow": "Kraków",
    "wroclaw": "Wrocław",
    "gdansk": "Gdańsk"
}

@dataclass
class ApartmentAd:
    external_id: str
    city: str
    price: float
    rooms: int | None
    sq_meters: float | None
    floor: int | None
    additional_rent: int | None
    district: str | None
    url: str
    title: str

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

async def parse_apartments_list(page: Page, city: str) -> list[ApartmentAd]:
    print(f"[{city.upper()}] Parsing apartments list...")
    try:
        await page.locator('[data-cy="l-card"]').first.wait_for(state="visible")
    except Exception:
        print(f"[{city.upper()}]Apartments list not found, end of the list or captcha")
        return []

    all_cards = await page.locator('[data-cy="l-card"]').all()
    print(f"Listings found on the page: {len(all_cards)}")

    results: list[ApartmentAd] = []

    for i, card in enumerate(all_cards):
        try:
            title_text = await card.locator('[data-testid="ad-card-title"] h4').inner_text(timeout=1000)

            link_element = card.locator('a').first
            raw_url = await link_element.get_attribute("href")
            url = "https://www.olx.pl" + raw_url if raw_url.startswith("/d/") else raw_url

            raw_price = await card.locator('[data-testid="ad-price"]').first.inner_text(timeout=1000)
            final_price = clean_price_text(raw_price)

            print(f"Parsed: {title_text} | Price: {final_price}")

            results.append(ApartmentAd(
                external_id=url,
                city=city,
                price=final_price,
                url=url,
                title=title_text,
                rooms=None,
                sq_meters=None,
                floor=None,
                additional_rent=None,
                district=None
            ))
        except Exception:
            print("Apartment not found")

    return results

async def parse_olx_details(page: Page, city: str) -> tuple[float | None, int | None, int | None, float | None, str | None]:
    sq_meters, rooms, floor,additional_rent,district = None, None, None, None, None

    try:
        area_element = page.locator("p").filter(has_text="Powierzchnia:").first
        await area_element.wait_for(state="visible", timeout=5000)
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
        clean_rent_text = rent_text.replace(" ", "")
        match = re.search(r'\d+[.,]?\d*', clean_rent_text)
        if match: additional_rent = float(match.group().replace(",", "."))
    except Exception:
        print ("Not found rent on this page")

    try:
        loc_element = page.locator("p").filter(has_text=CITY_DISPLAY_NAMES[city]).first
        await loc_element.wait_for(state="visible", timeout=2000)
        loc_text = await loc_element.inner_text()
        if "," in loc_text:
            parts = loc_text.split(",")
            if len(parts) > 1:
                district = parts[1].strip()
    except Exception:
        print("Not found district on this page")

    return sq_meters, rooms, floor, additional_rent, district

async def parse_otodom_details(page: Page, city: str) -> tuple[float | None, int | None, int | None, float | None, str | None]:
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
        rent_element = page.locator('div:text-is("Czynsz:") + div').first
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

        if CITY_DISPLAY_NAMES[city] in loc_text:
            parts = loc_text.split(",")
            if len(parts) > 1:
                district = parts[1].strip()
    except Exception:
        print("Not found district on this page")

    return sq_meters, rooms, floor, additional_rent, district

async def get_apartment_details(page: Page, apt: ApartmentAd) -> None:
    print(f"[{apt.city.upper()}] Entry inside: {apt.url}")
    try:
        await page.goto(apt.url, wait_until="domcontentloaded")
        await page.wait_for_timeout(1500)

        sq_meters, rooms, floor, additional_rent, district = None, None, None, None, None

        if "olx.pl" in apt.url:
            sq_meters, rooms, floor,additional_rent, district = await parse_olx_details(page, apt.city)
        elif "otodom.pl" in apt.url:
            sq_meters, rooms, floor,additional_rent, district = await parse_otodom_details(page,apt.city)

        print(f"[{apt.city.upper()}] -> Area: {sq_meters} m2 | Rooms: {rooms} | Floor: {floor}")

        apt.sq_meters = sq_meters
        apt.rooms = rooms
        apt.floor = floor
        apt.additional_rent = additional_rent
        apt.district = district

    except Exception as e:
        print(f"[{apt.city.upper()}] Error: {apt.url}: {e}")

async def scrape_city(browser, city: str) -> list[ApartmentAd]:
    print(f"Scraping cities: {city.capitalize()}")

    context = await browser.new_context(
        viewport={'width': 1280, 'height': 800},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        permissions=[]
    )

    page = await context.new_page()
    second_page = await context.new_page()
    all_parsed_apartments: list[ApartmentAd] = []
    MAX_PAGES = 5

    for current_page in range(1, MAX_PAGES + 1):
        print(f"[{city.capitalize()}] Page {current_page} of {MAX_PAGES}")
        city_url = city.lower()

        if current_page == 1:
            url = f"https://www.olx.pl/nieruchomosci/mieszkania/wynajem/{city_url}/"
        else:
            url = f"https://www.olx.pl/nieruchomosci/mieszkania/wynajem/{city_url}/?page={current_page}"

        await asyncio.sleep(random.uniform(2.0, 4.0))
        await page.goto(url, wait_until="domcontentloaded")

        if current_page == 1:
            await dismiss_popups(page)

        page_data = await parse_apartments_list(page, city)

        for apt in page_data:
            await asyncio.sleep(random.uniform(1.0, 2.5))
            await get_apartment_details(second_page, apt)
            all_parsed_apartments.append(apt)

    await context.close()
    return all_parsed_apartments

async def scrape_city_with_semaphore(browser, city: str, semaphore: asyncio.Semaphore) -> list[ApartmentAd]:
    async with semaphore:
        return await scrape_city(browser, city)

async def run_all_scrapers(cities: list[str]) -> list[ApartmentAd]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        semaphore = asyncio.Semaphore(2)

        tasks = [scrape_city_with_semaphore(browser, city, semaphore) for city in cities]
        results = await asyncio.gather(*tasks)

        await browser.close()

        all_apartments = []
        for city_results in results:
            all_apartments.extend(city_results)

        return all_apartments
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def _post_apartment(client: httpx.AsyncClient, payload: dict) -> httpx.Response:
    return await client.post(API_URL, json=payload)

async def send_apartments_to_api(apartments: list[ApartmentAd]) -> None:
    async with httpx.AsyncClient(headers={"X-API-KEY": settings.API_KEY}) as client:
        for apt in apartments:
            payload = {
                "url": apt.url,
                "title": apt.title,
                "city": apt.city,
                "district": apt.district,
                "price": apt.price,
                "additional_rent": apt.additional_rent,
                "sq_meters": apt.sq_meters,
                "rooms": apt.rooms,
                "floor": apt.floor,
            }
            try:
                response = await _post_apartment(client, payload)
                if response.status_code == 200:
                    print("Success!")
                elif response.status_code == 422:
                    print(f"Validation error for {apt.url}: {response.text}")
                elif response.status_code == 409:
                    print(f"Already in database: {apt.url}")
                else:
                    print("Error!")
            except Exception as e:
                print(f"Unexpected error:  {e}")

if __name__ == "__main__":
    cities_to_scrape = ["warszawa", "krakow", "wroclaw", "poznan", "gdansk"]
    results = asyncio.run(run_all_scrapers(cities_to_scrape))
    asyncio.run(send_apartments_to_api(results))
    print(f"\n Ready! Total count of apartments: {len(results)}")
