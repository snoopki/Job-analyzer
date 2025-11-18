import psycopg2
import logging
import os
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """Return a PostgreSQL connection."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.Error as e:
        logger.critical(f"Database connection failed: {e}")
        return None


def get_or_create_id(cursor, table, column_prefix, value, cache=None):
    """
    Return an existing ID from a lookup table or create a new one.
    Supports optional in-memory caching for performance.
    """
    if not value or value == "N/A":
        return None

    if cache is not None and value in cache:
        return cache[value]

    name_field = f"{column_prefix}_name"
    id_field = f"{column_prefix}_id"

    try:
        cursor.execute(
            f"SELECT {id_field} FROM {table} WHERE {name_field} = %s",
            (value,)
        )
        result = cursor.fetchone()

        if result:
            entity_id = result[0]
        else:
            cursor.execute(
                f"INSERT INTO {table} ({name_field}) VALUES (%s) RETURNING {id_field}",
                (value,)
            )
            entity_id = cursor.fetchone()[0]

        if cache is not None:
            cache[value] = entity_id

        return entity_id

    except psycopg2.Error as e:
        logger.error(f"get_or_create_id failed for {table} value='{value}': {e}")
        return None