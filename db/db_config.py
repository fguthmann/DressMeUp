import os

# Database connection parameters
db_params = {
    "dbname": os.getenv("DATABASE_NAME", 'mywardrobe'),
    "user": os.getenv("DATABASE_USER", 'postgres'),
    "password": os.getenv("DATABASE_PASSWORD", 'mysecretpassword'),
    "host": os.getenv("DATABASE_HOST", 'localhost')  # Default to 'localhost' if not set
}
