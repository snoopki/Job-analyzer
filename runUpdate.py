import time
import os
import traceback
import logging
from dotenv import load_dotenv
load_dotenv()
from jobScraper.controller import run_scraper
from analyzer.dbLoader import load_raw_data_to_db, create_schema
from analyzer import skillProcessor
from analyzer.dbCore import get_db_connection
from config import SEARCH_QUERY, JSONL_OUTPUT_FILE

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def ensure_schema():
    """Ensure database schema exists."""
    try:
        with get_db_connection() as conn:
            if conn is None:
                logger.critical("DB connection unavailable.")
                return False
            cursor = conn.cursor()
            create_schema(cursor)
            conn.commit()
            return True
    except Exception as e:
        logger.critical(f"Schema creation error: {e}", exc_info=True)
        return False


def run_full_update():
    """Run the full ETL process."""
    logger.info("Starting full update...")
    start = time.time()

    try:
        if not ensure_schema():
            logger.critical("Update aborted: schema init failed.")
            return

        run_scraper(SEARCH_QUERY)

        if not os.path.exists(JSONL_OUTPUT_FILE):
            logger.error(f"Output file not found: {JSONL_OUTPUT_FILE}")
            return

        load_raw_data_to_db()
        skillProcessor.run_skill_processor()

        logger.info(f"Update completed in {time.time() - start:.1f} seconds.")
    except Exception as e:
        logger.critical(f"Update crashed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    run_full_update()