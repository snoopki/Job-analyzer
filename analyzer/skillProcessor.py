import time
import re
import json
import logging
from pathlib import Path
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed

from . import dbQueries

MAX_WORKERS = 10

@lru_cache(maxsize=1)
def _load_skill_keywords() -> dict:
    json_path = Path(__file__).parent / "skill_keywords.json"
    if not json_path.exists():
        logging.error(f"Missing required file: {json_path}")
        raise FileNotFoundError(f"Missing required file: {json_path}")
    
    data = json_path.read_text(encoding="utf-8")
    
    try:
        data_json = json.loads(data)
        logging.info(f"skill_keywords.json loaded – {len(data_json)} skill categories.")
        return data_json
    except json.JSONDecodeError as e:
        logging.error(f"Corrupt skill_keywords.json file: {e}")
        raise ValueError(f"Corrupt skill_keywords.json file: {e}") from e

@lru_cache(maxsize=1)
def _get_compiled_skill_engine() -> list:
    logging.info("Building skill engine (Regex) for the first time...")
    
    SKILL_KEYWORDS = _load_skill_keywords()
    COMPILED_SKILLS = []

    def expand_synonyms_list(raw_list):
        out = set()
        for item in raw_list:
            if not isinstance(item, str):
                continue
            parts = [p.strip() for p in item.split(',') if p.strip()]
            out.update(parts)
        return list(out)

    for canonical_name, synonyms in SKILL_KEYWORDS.items():
        expanded_synonyms = expand_synonyms_list(synonyms)
        expanded_synonyms = sorted(list(set(expanded_synonyms)), key=lambda s: -len(s))

        patterns = []
        for s in expanded_synonyms:
            if not s:
                continue
            escaped_s = re.escape(s)

            if canonical_name == 'c' and s.lower() == 'c':
                pattern = r'(?<![\w\+#])' + escaped_s + r'(?![\w#\+])'
            else:
                pattern = r'(?<![\w-])' + escaped_s + r'(?![\w-])'
            
            patterns.append(pattern)

        if patterns:
            full_pattern = r'(?:' + '|'.join(patterns) + r')'
            COMPILED_SKILLS.append((canonical_name, re.compile(full_pattern, re.IGNORECASE)))

    logging.info(f"Skill engine built: {len(COMPILED_SKILLS)} canonical skills ready for scanning.")
    return COMPILED_SKILLS

def extract_skills_from_text(job_id, description) -> tuple:
    if not description:
        return job_id, []

    COMPILED_SKILLS = _get_compiled_skill_engine()
    
    found_skills_canonical = set()

    for canonical_name, regex_pattern in COMPILED_SKILLS:
        if regex_pattern.search(description):
            found_skills_canonical.add(canonical_name)

    return job_id, list(found_skills_canonical)

def run_skill_processor():
    logging.info("Starting Stage 3: Skill Processing (Keyword Processor)...")

    jobs_to_process = dbQueries.get_jobs_to_process()

    if not jobs_to_process:
        logging.info("No jobs found in DB. Process stopped.")
        return

    start_time = time.time()
    results_dict = {}
    processed_count = 0
    total_jobs = len(jobs_to_process)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        logging.info(f"Scanning {total_jobs} job descriptions using {MAX_WORKERS} workers...")
        
        future_to_job = {
            executor.submit(extract_skills_from_text, job_id, desc): job_id
            for job_id, desc in jobs_to_process
        }

        for future in as_completed(future_to_job):
            try:
                job_id, skills_list = future.result()
                results_dict[job_id] = skills_list
                processed_count += 1
                
                if processed_count % 20 == 0 or processed_count == total_jobs:
                    logging.info(f"    ...Processing: {processed_count}/{total_jobs} completed.")
            except Exception as e:
                job_id = future_to_job[future]
                logging.error(f"Error processing job_id {job_id}: {e}")

    scan_end_time = time.time()
    logging.info(f"Text scanning complete in {scan_end_time - start_time:.2f} seconds.")

    logging.info("Saving results to DB...")
    save_success = dbQueries.save_processed_skills(results_dict)

    elapsed = time.time() - start_time
    logging.info("-" * 50)
    if save_success:
        logging.info(f"Skill processing finished successfully! Total time: {elapsed:.2f} seconds")
    else:
        logging.warning(f"Save failed - check logs. Total time: {elapsed:.2f} seconds")
    logging.info(f"Successfully processed {len(results_dict)} jobs.")
    logging.info("-" * 50)