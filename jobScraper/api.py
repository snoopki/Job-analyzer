import requests
import time
import logging
from jobSearchConfig import BASE_URL, API_SEARCH_PATH, build_api_params, MAIN_CATEGORIES

logger = logging.getLogger(__name__)

class ApiClient:
    def __init__(self, search_config):
        self.base_url = BASE_URL
        self.search_path = API_SEARCH_PATH
        self.search_config = search_config
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/100.0.0.0 Safari/537.36'
            ),
            'Accept': 'application/json, text/plain, */*',
            'Referer': (
                f'{self.base_url}/jobs/cat'
                f'{MAIN_CATEGORIES.get(self.search_config["main_category"], "")}/?ssaen=3'
            ),
        }

    def fetch_page(self, page_num, retries=3):
        params = build_api_params(
            main_category_key=self.search_config["main_category"],
            subcategories_keys=self.search_config["roles"],
            experience_key=self.search_config["experience"],
            search_term_key=self.search_config["keyword"],
            page=page_num,
        )

        api_url = f"{self.base_url}{self.search_path}"
        logger.debug(f"ApiClient sending request for page {page_num} with params={params}")

        for attempt in range(retries):
            try:
                response = requests.get(
                    api_url,
                    params=params,
                    headers=self.headers,
                    timeout=(3, 5),
                )
                response.raise_for_status()
                return response.json()

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.warning(
                    f"Timeout/connection error on attempt {attempt+1}/{retries} "
                    f"for page {page_num}: {e}"
                )
                time.sleep(0.5)

            except requests.exceptions.RequestException as e:
                logger.error(
                    f"HTTP error for page {page_num}: {e}. Aborting this page."
                )
                return None

            except Exception as e:
                logger.error(
                    f"Unexpected error in fetch_page for page {page_num}: {e}",
                    exc_info=True,
                )
                return None

        logger.error(f"All {retries} attempts failed for page {page_num}.")
        return None