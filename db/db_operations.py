import psycopg2
from psycopg2.extras import execute_batch
from .db_config import db_params

def create_connection():
    return psycopg2.connect(**db_params)

def create_tables():
    conn = create_connection()
    cur = conn.cursor()
    clothing_types = ['bag', 'dress', 'hat', 'jacket', 'pant', 'shirt', 'shoe', 'short', 'skirt']
    for clothing_type in clothing_types:
        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {clothing_type} (
            id SERIAL PRIMARY KEY,
            image_url VARCHAR(255)
        );
        """)
    conn.commit()
    cur.close()
    conn.close()

def insert_items(clothing_type, items):
    conn = create_connection()
    cur = conn.cursor()
    query = f"INSERT INTO {clothing_type} (image_url) VALUES (%s);"
    execute_batch(cur, query, [(item,) for item in items])
    conn.commit()
    cur.close()
    conn.close()
