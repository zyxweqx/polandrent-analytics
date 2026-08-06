import asyncio

import pandas as pd
from sqlalchemy import create_engine

from app.core.config import settings
from app.services.notifier import send_tg_message


def _sync_database_url() -> str:
    return settings.DATABASE_URL.replace("+asyncpg", "+psycopg2")


def run_analytics() -> None:
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 40)

    engine = create_engine(_sync_database_url())
    df = pd.read_sql_query("SELECT * FROM apartments", engine)

    if df.empty:
        print("No apartments in the database yet, nothing to analyze.")
        return

    df['additional_rent'] = df['additional_rent'].fillna(0)
    df['total_price'] = df['price'] + df['additional_rent']

    df_clean = df.dropna(subset=['district', 'sq_meters'])
    df_clean = df_clean[df_clean['sq_meters'] > 0]
    df_clean = df_clean[df_clean['district'] != 'wielkopolskie']
    df_clean = df_clean.drop_duplicates(subset=['title'])
    df_clean = df_clean[~df_clean['title'].str.contains(r'(?i)pok[oó]j', na=False, regex=True)]
    df_clean['price_per_sqm'] = df_clean['total_price'] / df_clean['sq_meters']

    print("Average price per district: ")
    stats = df_clean.groupby('district')['total_price'].mean().sort_values(ascending=False)
    print(stats)

    if df_clean.empty:
        print("Nothing left after cleaning, skipping the Telegram report.")
        return

    message_lines = ["\n- Top 5 the cheapest apartments per m² -"]
    top_5 = df_clean.sort_values(by='price_per_sqm').head(5)

    for _, row in top_5.iterrows():
        apt_block = (
            f"🏢 <b>{row['title']}</b>\n"
            f"📍 District: {row['district']}\n"
            f"💰 Price: {row['total_price']:.0f} zł (<i>{row['price_per_sqm']:.2f} zł/м²</i>)\n"
            f"🔗 <a href='{row['url']}'>Open url</a>\n"
            f"{'—' * 20}"
        )
        message_lines.append(apt_block)
        print(f"Ready: {row['title']}")

    final_text = "\n".join(message_lines)

    if not settings.TELEGRAM_CHAT_ID:
        print("TELEGRAM_CHAT_ID is not set, skipping Telegram report.")
        return

    asyncio.run(send_tg_message(settings.TELEGRAM_CHAT_ID, final_text))


if __name__ == '__main__':
    run_analytics()
