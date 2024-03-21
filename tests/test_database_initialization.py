import pytest
import psycopg2
from app.initialization_database import db_params, initialize_database

# Update expected tables with 'table_' prefix as per the updated naming convention
EXPECTED_TABLES = ['table_bag', 'table_dress', 'table_hat', 'table_jacket', 'table_pants', 'table_shirt', 'table_shoe',
                   'table_short', 'table_skirt']


def check_table_exists(conn, table_name):
    """Check if a table exists in the database."""
    cur = conn.cursor()
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = %s
        );
    """, (table_name,))
    exists, = cur.fetchone()
    cur.close()
    return exists


@pytest.fixture(scope="module")
def db_connection():
    """Database connection fixture."""
    conn = psycopg2.connect(**db_params)
    # Initialize database (create tables)
    initialize_database()
    yield conn
    # Cleanup: close database connection
    conn.close()


def test_initialize_database(db_connection):
    """Test that all expected tables are created by initialize_database."""
    for table_name in EXPECTED_TABLES:
        assert check_table_exists(db_connection, table_name), f"Table '{table_name}' does not exist."
