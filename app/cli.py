import asyncio

import typer

from app.services.analytics import run_analytics
from app.services.scraper import run_all_scrapers, send_apartments_to_api

app = typer.Typer()


@app.command()
def scrape(city: str = typer.Option(None, help="The city to scrape")):
    if city:
        cities = [city]
    else:
        cities = ["warszawa", "krakow", "wroclaw", "poznan", "gdansk"]

    results = asyncio.run(run_all_scrapers(cities))
    asyncio.run(send_apartments_to_api(results))

@app.command()
def analytics():
    run_analytics()

if __name__ == "__main__":
    app()
