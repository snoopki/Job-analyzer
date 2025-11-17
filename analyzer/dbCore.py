import sqlite3
import logging
from config import DB_FILE_PATH

logger = logging.getLogger(__name__)


def get_db_connection():
    """Return a SQLite connection with foreign keys enabled."""
    try:
        conn = sqlite3.connect(DB_FILE_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
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
            f"SELECT {id_field} FROM {table} WHERE {name_field} = ?",
            (value,)
        )
        result = cursor.fetchone()

        if result:
            entity_id = result[0]
        else:
            cursor.execute(
                f"INSERT INTO {table} ({name_field}) VALUES (?)",
                (value,)
            )
            entity_id = cursor.lastrowid

        if cache is not None:
            cache[value] = entity_id

        return entity_id

    except sqlite3.Error as e:
        logger.error(f"get_or_create_id failed for {table} value='{value}': {e}")
        return None
