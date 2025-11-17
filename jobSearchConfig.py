import logging
from urllib.parse import quote_plus

BASE_URL = "https://www.drushim.co.il"
API_SEARCH_PATH = "/api/jobs/search"

logger = logging.getLogger(__name__)

MAIN_CATEGORIES = {
    "hitech_software": "6",
    "hitech_hardware": "4",
    "hitech_qa": "24",
    "hitech_general": "5",
}

SUBCATEGORIES = {
    "backend": "616",
    "bi_data_science": "70",
    "cloud": "546",
    "data_analyst": "581",
    "devops": "491",
    "full_stack": "504",
    "ai_developer": "703",
    "sw_architect": "465",
    "sw_engineer": "380",
    "system_analyst": "235",
    "team_lead_dev": "315",
    "erp_crm_dev": "73",
    "rt_embedded": "67",
    "hitech_general_sub": "209",
    "qa_manual": "297",
    "qa_automation": "306",
    "qa_engineer": "299",
}


EXPERIENCE_LEVELS = {
    "no_experience": "0",
    "junior": "1-2",
    "mid": "3-4",
    "senior": "5-6",
    "expert": "7",
}

SEARCH_TERMS = {
    "software_development": "פיתוח תוכנה",
    "qa": "בדיקות תוכנה",
    "data": "נתונים",
}


def build_api_params(
    main_category_key=None,
    subcategories_keys=None,
    experience_key=None,
    search_term_key=None,
    page=1,
):
    """
    Builds a dictionary of query parameters for the API GET call.
    """

    params = {
        "ssaen": "3",
        "isAA": "true",
    }

    main_cat_code = MAIN_CATEGORIES.get(main_category_key)
    valid_subcat_keys = [
        key for key in (subcategories_keys or []) if key in SUBCATEGORIES
    ]
    subcat_codes = "-".join([SUBCATEGORIES[key] for key in valid_subcat_keys])

    if subcat_codes:
        params["subcat"] = subcat_codes
    elif main_cat_code:
        params["catdir"] = main_cat_code

    exp_code = EXPERIENCE_LEVELS.get(experience_key) if experience_key else None
    if exp_code is not None:
        params["experience"] = exp_code

    search_term = SEARCH_TERMS.get(search_term_key) if search_term_key else None
    if search_term is not None:
        params["searchterm"] = quote_plus(search_term)

    params["page"] = page

    logger.debug(f"API params for page {page}: {params}")
    return params
