from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from config import DATABASE

def get_engine()-> Engine:
    """
    Create and return a SQLAlchemy Engine instance
    using the database configuration defined in DATABASE.

    The configuration dictionary must contain:
        - drivername
        - username
        - password
        - host
        - port
        - database

    Returns:
        Engine: A SQLAlchemy Engine object responsible
        for managing database connections and executing queries.
    """
    url = URL.create(**DATABASE)
    return create_engine(url)