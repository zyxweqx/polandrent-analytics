import os

import pandas as pd
import sqlite3 as sql

def run_analytics():
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 40)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, '..', '..', 'polandrent.db')
    conn = sql.connect(db_path)

    df = pd.read_sql_query("SELECT * FROM apartments", conn)

    df['additional_rent'] = df['additional_rent'].fillna(0)
    df['total_price'] = df['price'] + df['additional_rent']
    df['price_per_sqm'] = df['total_price'] / df['sq_meters']

    print("Average price per district: ")
    stats = df.groupby('district')['total_price'].mean().sort_values(ascending=False)
    print(stats)

    df_clean = df.dropna(subset=['district'])
    df_clean = df_clean[df_clean['district'] != 'wielkopolskie']

    df_clean = df_clean.drop_duplicates(subset=['title'])

    df_clean = df_clean[~df_clean['title'].str.contains(r'(?i)pok[oó]j', na=False, regex=True)]
    print("\n- Top 5 the cheapest apartments per m² -")
    top_5 = df_clean.sort_values(by='price_per_sqm').head(5)

    for index, row in top_5.iterrows():
        print(f"Title: {row['title']}")
        print(f" District: {row['district']} | 💰 Price per m²: {row['price_per_sqm']:.2f} zł")
        print(f" URL: {row['url']}")

if __name__ == '__main__':
    run_analytics()