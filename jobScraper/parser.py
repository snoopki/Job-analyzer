from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)


def clean_html(raw_html):
    if not raw_html:
        return ""

    raw_html = raw_html.replace("<br/>", "<br>")

    soup = BeautifulSoup(raw_html, 'html.parser')
    for br in soup.find_all("br"):
        br.replace_with("\n")

    text = soup.get_text(separator="\n", strip=True)
    return re.sub(r'\n\s*\n+', '\n', text)


def extract_jobs_from_page(data, base_url):
    jobs = []
    if not data:
        logger.warning("Parser: קיבל 'data=None', מחזיר רשימה ריקה.")
        return jobs

    job_list = data.get('ResultList', [])
    for job_item in job_list:
        if not isinstance(job_item, dict):
            logger.warning(f"Parser: נמצא פריט 'job_item' שאינו dict. מדלג. תוכן: {str(job_item)[:50]}...")
            continue

        job_content = job_item.get('JobContent', {})
        company_data = job_item.get('Company', {})
        job_info = job_item.get('JobInfo', {})

        job_title = job_content.get('Name', 'N/A')
        company_name = company_data.get('CompanyDisplayName', 'N/A')
        experience_text = job_content.get('Experience', {}).get('NameInHebrew', 'N/A')
        relative_link = job_info.get('Link')
        full_link = f"{base_url}{relative_link}" if base_url and relative_link else 'N/A'

        description_html = job_content.get('Description', '')
        requirements_html = job_content.get('Requirements', '')
        clean_description = clean_html(description_html)
        clean_requirements = clean_html(requirements_html)

        full_description = []
        if clean_description:
            full_description.append("תיאור משרה:\n" + clean_description)
        if clean_requirements:
            full_description.append("\nדרישות:\n" + clean_requirements)

        locations_list = []
        locations_data = job_content.get('Addresses', [])
        if isinstance(locations_data, list) and locations_data:
            city_names = [loc.get('City', '') for loc in locations_data if isinstance(loc, dict) and loc.get('City')]
            unique_cities = list(dict.fromkeys(filter(None, city_names)))
            locations_list = unique_cities
            if not locations_list:
                regions_data = job_content.get('Regions', [])
                if isinstance(regions_data, list) and regions_data:
                    region_names = [reg.get('NameInHebrew', '') for reg in regions_data if isinstance(reg, dict) and reg.get('NameInHebrew')]
                    locations_list = list(dict.fromkeys(filter(None, region_names)))

        jobs.append({
            'title': job_title.strip() if job_title else 'N/A',
            'company': company_name.strip() if company_name else 'N/A',
            'locations': locations_list,
            'experience': experience_text.strip() if experience_text else 'N/A',
            'description': "\n".join(full_description).strip(),
            'link': full_link
        })

    return jobs
