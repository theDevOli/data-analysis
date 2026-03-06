import os
from dotenv import load_dotenv

load_dotenv()

DATABASE = {
    "drivername": os.getenv("DB_DRIVER"),
    "username": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "database": os.getenv("DB_NAME"),
}
OUTPUT_PATH = "output/offices"