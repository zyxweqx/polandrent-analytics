import pytest
import pytest_asyncio
from playwright.async_api import async_playwright

from app.services.scraper import parse_olx_details, parse_otodom_details


@pytest_asyncio.fixture
async def browser_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        yield page
        await browser.close()

@pytest.fixture
def olx_html():
    with open("tests/fixtures/olx_sample.html",encoding="utf-8") as f:
        return f.read()

@pytest.fixture
def otodom_html():
    with open("tests/fixtures/otodom_sample.html",encoding="utf-8") as f:
        return f.read()

async def test_parse_olx_details_fixture(browser_page, olx_html):
    await browser_page.set_content(olx_html)
    sq_meters, rooms, floor, additional_rent, district = await parse_olx_details(browser_page, "poznan")
    assert sq_meters == 50
    assert rooms == 2
    assert floor == 2
    assert additional_rent == 1500
    assert district == "Jeżyce"

async def test_parse_otodom_details_fixture(browser_page, otodom_html):
    await browser_page.set_content(otodom_html)
    sq_meters, rooms, floor, additional_rent, district = await parse_otodom_details(browser_page, "poznan")
    assert sq_meters == 20
    assert rooms == 1
    assert floor == 2
    assert additional_rent == 550
    assert district == "Centrum"
