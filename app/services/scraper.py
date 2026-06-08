import asyncio
from playwright.async_api import async_playwright
from app.core.database import async_session_maker
from app.models.apartments import Apartment
from sqlalchemy import select


def clean_price_text(raw_price: str) -> float:
        clean_price = raw_price.replace(" ", "").replace("zł", "").replace("donegocjacji", "").replace("\n","").replace(",", ".")
        final_price = float(clean_price)
        return final_price

async def dismiss_popups(page):
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

async def parse_apartments_list(page):
    print("Parsing apartments list...")
    await page.locator('[data-cy="l-card"]').first.wait_for(state="visible")
    all_cards = await page.locator('[data-cy="l-card"]').all()
    print(f"Listings found on the page: {len(all_cards)}")

    results = []

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

async def save_to_db(apartments_data):
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
                city=apt_data["city"]
            )
            session.add(new_apt)
            added_count += 1
        print(f"Committing to the database... (Added: {added_count}, Skipped: {skipped_count})")
        await session.commit()

async def run_scraper():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            permissions=[]
        )
        page = await context.new_page()

        await page.goto("https://www.olx.pl/nieruchomosci/mieszkania/wynajem/poznan/", wait_until="networkidle")

        await dismiss_popups(page)

        apartments_data = await parse_apartments_list(page)

        await save_to_db(apartments_data)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
