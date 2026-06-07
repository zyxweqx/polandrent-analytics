import asyncio

from playwright.async_api import async_playwright


async def run_scraper():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            permissions=[]
        )
        page = await context.new_page()

        await page.goto("https://www.olx.pl/nieruchomosci/mieszkania/wynajem/poznan/", wait_until="networkidle")

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

        all_cards = await page.locator('[data-cy="l-card"]').all()

        print(f"Listings found on the page: {len(all_cards)}")

        for i, card in enumerate(all_cards):
            try:
                title_text = await card.locator('[data-testid="ad-card-title"] h4').inner_text(timeout=1000)
                price_text = await card.locator('[data-testid="ad-price"]').inner_text(timeout=1000)
                price_text = price_text.replace("\n", "").strip()
                print(f"Name: {title_text} | Price: {price_text}")
            except Exception as e:
                if i < 5:
                    print(f"Card {i+1} skipped. Reason: {type(e).__name__}")
                continue
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())