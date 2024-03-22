import psycopg2
import logging

# Database connection parameters
db_params = {
    "dbname": "mywardrobe",
    "user": "postgres",
    "password": "mysecretpassword",
    "host": "db"
}

def initialize_database():
    logging.info("Starting database initialization")
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        
        clothing_types = ['bag', 'dress', 'hat', 'jacket', 'pants', 'shirt', 'shoe', 'short', 'skirt']
        for clothing_type in clothing_types:
            table_name = f"table_{clothing_type}"
            cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                image_data BYTEA
            );
            """)
            logging.info(f"Table {table_name} created or already exists")
        conn.commit()
        logging.info("Database initialization completed successfully")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        if conn is not None:
            conn.rollback()
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
