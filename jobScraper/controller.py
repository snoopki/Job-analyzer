import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from .api import ApiClient
from .parser import extract_jobs_from_page
from .storage import StreamingJsonlWriter
from config import JSONL_OUTPUT_FILE

logger = logging.getLogger(__name__)

MAX_CONCURRENT_WORKERS = 15
MAX_PAGES_TO_FETCH = 80


def run_scraper(search_config):
    filename = JSONL_OUTPUT_FILE

    logger.info("Scraper started")
    logger.info(f"Search config: {search_config}")

    api_client = ApiClient(search_config)

    first_page = api_client.fetch_page(1)
    if not first_page:
        logger.error("Failed to fetch page 1. Aborting.")
        return

    total_api_pages = first_page.get("TotalPagesNumber", 0)
    total_jobs = first_page.get("TotalSearchResultCount", 0)

    logger.info(f"API reports {total_jobs} jobs across {total_api_pages} pages.")

    if total_api_pages == 0:
        logger.warning("API returned 0 pages. Aborting.")
        return

    pages_to_process = min(total_api_pages, MAX_PAGES_TO_FETCH)
    logger.info(f"Processing {pages_to_process} pages (limit: {MAX_PAGES_TO_FETCH}).")

    total_collected = 0
    start_time = time.time()

    try:
        with StreamingJsonlWriter(filename) as writer:
            logger.info("Processing page 1...")
            jobs_page_1 = extract_jobs_from_page(first_page, api_client.base_url)
            writer.write_rows(jobs_page_1)
            total_collected += len(jobs_page_1)

            pages_to_fetch = list(range(2, pages_to_process + 1))

            if pages_to_fetch:
                logger.info(f"Dispatching {len(pages_to_fetch)} pages to ThreadPool ({MAX_CONCURRENT_WORKERS} workers).")

                with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_WORKERS) as executor:
                    future_to_page = {
                        executor.submit(api_client.fetch_page, page): page
                        for page in pages_to_fetch
                    }

                    for future in as_completed(future_to_page):
                        page_num = future_to_page[future]
                        try:
                            data = future.result()
                            if data:
                                jobs = extract_jobs_from_page(data, api_client.base_url)
                                if jobs:
                                    writer.write_rows(jobs)
                                    total_collected += len(jobs)

                        except Exception as e:
                            logger.error(f"Failed processing page {page_num}: {e}", exc_info=False)

    except Exception as e:
        logger.critical(f"Critical failure during scraping: {e}", exc_info=True)
        return

    elapsed = time.time() - start_time
    logger.info("Scraper finished")
    logger.info(f"Collected total {total_collected} jobs in {elapsed:.2f} seconds.")
