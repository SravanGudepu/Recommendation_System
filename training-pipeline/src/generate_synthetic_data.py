"""
Generate products, users and events. 
Connect PostgreSQL and insert data into tables.
"""

import random
import uuid
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch

## Configuration

DB_CONFIG = {
    "dbname": "recsys",
    "user": "saivenkatasravangudepu",
    "host": "localhost",
    "port": 5432
}

NUM_PRODUCTS = 30
NUM_USERS = 10
NUM_EVENTS = 25000

random.seed(12)
np.random.seed(12)

# Domain dictionaries

CATEGORY_MAP = {
    "Electronics": {
        "subcategories": ["Headphones", "Phones", "Laptops", "Accessories"],
        "brands": ["Sony", "Apple", "Samsung", "Bose", "Dell"]
    },
    "Footwear":{
        "subcategories": ["Running Shoes", "Sneakers", "Sandals", "Boots"],
        "brands": ["Nike", "Adidas", "Puma", "Reebok", "Skechers"]
    },
    "Clothing": {
        "subcategories": ["T-Shirts", "Jeans", "Jackets", "Activewear"],
        "brands": ["Levis", "H&M", "Zara", "Uniqlo", "Nike"]
    },
    "Home": {
        "subcategories": ["Furniture", "Decor", "Kitchen", "Storage"],
        "brands": ["IKEA", "Targethome", "HomeEssentials", "OXO", "Pyrex"]
    },
    "Beauty": {
        "subcategories": ["Skincare", "Makeup", "Haircare", "Fragrance"],
        "brands": ["L'Oreal", "Maybelline", "Neutrogena", "CeraVe", "Nivea"]
    },
    "Grocery": {
        "subcategories": ["Snacks", "Beverages", "Pantry", "Frozen"],
        "brands": ["Kelloggs", "Pepsi", "CocaCola", "Nestle", "GeneralMills"]
    },
    "Sports":{
        "subcategories": ["Fitness", "Outdoor", "Cycling", "Team Sports"],
        "brands": ["Nike", "Adidas", "Under Armour", "Wilson", "Spalding"]
    }
}

USER_SEGMENTS = ["new", "regular", "premium"]
REGIONS = ["Texas", "California", "New York", "Florida", "Illinois", "Michigan"]
INVENTORY_STATUSES = ["in_stock", "low_stock", "out_of_stock"]
SOURCES = ["app", "web"]

# Product Generation

def generate_products(num_products: int):
    products = []

    categories = list(CATEGORY_MAP.keys())

    for i in range(1, num_products + 1):
        category = random.choice(categories)
        subcategory = random.choice(CATEGORY_MAP[category]["subcategories"])
        brand = random.choice(CATEGORY_MAP[category]["brands"])

        price = round(random.uniform(5, 1500), 2)
        rating = round(random.uniform(2.5, 5.0), 1)
        inventory_status = random.choices(
            INVENTORY_STATUSES, weights=[0.8, 0.15, 0.05], k=1
        )[0]

        popularity_score = round(random.uniform(0.1, 1.0), 4)

        product_id = f"p{i}"
        name = f"{brand} {subcategory} {i}"

        products.append((
            product_id,
            name,
            category,
            subcategory,
            brand,
            price,
            rating,
            inventory_status,
            popularity_score
        ))

    return products

# User Generation

def generate_users(num_users: int):
    users = []
    categories = list(CATEGORY_MAP.keys())

    for i in range(1, num_users + 1):
        user_id = f"u{i}"
        segment = random.choices(USER_SEGMENTS, weights=[0.25, 0.55, 0.20], k=1)[0]
        region = random.choice(REGIONS)
        preferred_category = random.choice(categories)

        users.append((
            user_id,
            segment,
            region,
            preferred_category
        ))

    return users

# Event Generation

def generate_events(num_events: int, users, products):
    events = []

    product_lookup = {}
    for p in products:
        product_lookup[p[0]] = {
            "category": p[2],
            "popularity_score": p[8],
            "inventory_status": p[7]
        }

    user_lookup = {u[0]: {"preferred_category": u[3]} for u in users}

    user_ids = [u[0] for u in users]
    product_ids = [p[0] for p in products]

    now = datetime.now()

    for _ in range(num_events):
        user_id = random.choice(user_ids)
        preferred_category = user_lookup[user_id]["preferred_category"]

        # Bias product choice toward preferred category
        if random.random() < 0.7:
            preferred_products = [
                pid for pid, pdata in product_lookup.items()
                if pdata["category"] == preferred_category
            ]
            product_id = random.choice(preferred_products) if preferred_products else random.choice(product_ids)
        else:
            product_id = random.choice(product_ids)

        event_type = random.choices(
            ["view", "click", "add_to_cart", "purchase"],
            weights=[0.55, 0.35, 0.13, 0.07],
            k=1
        )[0]

        # Spread timestamps over last 90 days
        days_ago = random.randint(0, 89)
        seconds_offset = random.randint(0, 86400)
        event_timestamp = now - timedelta(days=days_ago, seconds=seconds_offset)


        session_id = f"s_{uuid.uuid4().hex[:10]}"
        source = random.choice(SOURCES)

        events.append((
            user_id,
            product_id,
            event_type,
            event_timestamp,
            session_id,
            source
        ))

    return events

# Database Insertion
def truncate_tables(conn):
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE events, users, products RESTART IDENTITY CASCADE;")
    conn.commit()

def insert_products(conn, products):
    query = """
        INSERT INTO products (
        product_id, name, category, subcategory, brand,
        price, rating, inventory_status, popularity_score
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
    with conn.cursor() as cur:
        execute_batch(cur, query, products, page_size=1000)
    conn.commit()

def insert_users(conn, users):
    query = """
        INSERT INTO users (
        user_id, segment, region, preferred_category
        )
        VALUES (%s, %s, %s, %s)
    """
    with conn.cursor() as cur:
        execute_batch(cur, query, users, page_size=1000)
    conn.commit()

def insert_events(conn, events):
    query = """
        INSERT INTO events (
        user_id, product_id, event_type, event_timestamp, session_id, source
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    with conn.cursor() as cur:
        execute_batch(cur, query, events, page_size=1000)
    conn.commit()

def main():
    print("Connecting to PostgreSQL")
    conn = psycopg2.connect(**DB_CONFIG)

    try:
        print("Truncating existing tables")
        truncate_tables(conn)

        print("Generating products")
        products = generate_products(NUM_PRODUCTS)

        print("Generating users")
        users = generate_users(NUM_USERS)

        print("Generating events")
        events = generate_events(NUM_EVENTS, users, products)

        print("Inserting products")
        insert_products(conn, products)

        print("Inserting users")
        insert_users(conn, users)

        print("Inserting events")
        insert_events(conn, events)

        print("Done")
        print(f"Inserted {len(products)} products")
        print(f"Inserted {len(users)} users")
        print(f"Inserted {len(events)} events")

    finally:
        conn.close()

if __name__ == "__main__":
    main()
