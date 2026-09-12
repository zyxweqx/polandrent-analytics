import pytest

from app.services.scraper import clean_price_text


@pytest.mark.parametrize("raw_price, expected", [
    ("2500 zł", 2500),
    ("2 500,50 zł", 2500.5),
    ("3 000 zł do negocjacji", 3000.0),
    (" \n 2 100 \n zł ", 2100.0),
    ("0 zł", 0.0),
])

def test_clean_price_text_valid_data(raw_price, expected):
    assert clean_price_text(raw_price) == expected

def test_clean_price_text_raises_error():
    with pytest.raises(ValueError):
        clean_price_text("Zadzwoń")
