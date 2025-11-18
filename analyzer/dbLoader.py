import json
import os
import logging
from config import JSONL_OUTPUT_FILE 
from .dbCore import get_db_connection, get_or_create_id 

logger = logging.getLogger(__name__)


def create_schema(cursor):
    logger.info("Verifying database schema...")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        company_id SERIAL PRIMARY KEY, 
        company_name TEXT NOT NULL UNIQUE
    );""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS experience_levels (
        level_id SERIAL PRIMARY KEY, 
        level_name TEXT NOT NULL UNIQUE
    );""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        job_id SERIAL PRIMARY KEY, 
        title TEXT, 
        description TEXT, 
        link TEXT, 
        scraped_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
        company_id INTEGER, 
        level_id INTEGER,
        FOREIGN KEY (company_id) REFERENCES companies (company_id),
        FOREIGN KEY (level_id) REFERENCES experience_levels (level_id)
    );""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS locations (
        location_id SERIAL PRIMARY KEY, 
        location_name TEXT NOT NULL UNIQUE
    );""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skills (
        skill_id SERIAL PRIMARY KEY, 
        skill_name TEXT NOT NULL UNIQUE
    );""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_skills (
        job_id INTEGER, 
        skill_id INTEGER,
        FOREIGN KEY (job_id) REFERENCES jobs (job_id) ON DELETE CASCADE,
        FOREIGN KEY (skill_id) REFERENCES skills (skill_id) ON DELETE CASCADE,
        PRIMARY KEY (job_id, skill_id)
    );""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_locations (
        job_id INTEGER, 
        location_id INTEGER,
        FOREIGN KEY (job_id) REFERENCES jobs (job_id) ON DELETE CASCADE,
        FOREIGN KEY (location_id) REFERENCES locations (location_id) ON DELETE CASCADE,
        PRIMARY KEY (job_id, location_id)
    );""")
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company_id ON jobs (company_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_level_id ON jobs (level_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_skills_name ON skills (skill_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_companies_name ON companies (company_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_locations_name ON locations (location_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_experience_name ON experience_levels (level_name);")


def load_raw_data_to_db():
    if not os.path.exists(JSONL_OUTPUT_FILE):
        logger.error(f"Error: {JSONL_OUTPUT_FILE} not found.")
        return False

    job_locations_to_insert = []
    company_cache = {}
    location_cache = {}
    level_cache = {}
    inserted_jobs_count = 0

    try:
        with open(JSONL_OUTPUT_FILE, 'r', encoding='utf-8') as f_json, \
             get_db_connection() as conn:
            
            if conn is None: 
                logger.error("DB Loader: Could not get DB connection.")
                return False
            
            cursor = conn.cursor()
            
            logger.info("DB Loader: Clearing old data...")
            cursor.execute("TRUNCATE TABLE jobs, job_skills, job_locations RESTART IDENTITY CASCADE;")
            
            logger.info(f"DB Loader: Starting raw data load from {JSONL_OUTPUT_FILE}...")
            
            for line in f_json:
                try:
                    job = json.loads(line)
                    company_id = get_or_create_id(cursor, "companies", "company", job.get('company'), company_cache)
                    level_id = get_or_create_id(cursor, "experience_levels", "level", job.get('experience'), level_cache)

                    cursor.execute("""
                    INSERT INTO jobs (title, description, link, company_id, level_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING job_id""", (
                        job.get('title'), job.get('description'), job.get('link'),
                        company_id, level_id
                    ))
                    job_id = cursor.fetchone()[0]
                    inserted_jobs_count += 1

                    locations_list = job.get('locations', [])
                    if not locations_list:
                        loc_name = "N/A"
                        location_id = get_or_create_id(cursor, "locations", "location", loc_name, location_cache)
                        if location_id: job_locations_to_insert.append((job_id, location_id))
                    else:
                        for loc_name in locations_list:
                            location_id = get_or_create_id(cursor, "locations", "location", loc_name, location_cache)
                            if location_id: job_locations_to_insert.append((job_id, location_id))
                                
                except json.JSONDecodeError:
                    logger.warning(f"JSON Decode Error: {line[:50]}...")
            
            if job_locations_to_insert:
                cursor.executemany("""
                    INSERT INTO job_locations (job_id, location_id) 
                    VALUES (%s, %s) 
                    ON CONFLICT DO NOTHING
                """, job_locations_to_insert)
            
            conn.commit()
            logger.info(f"DB Loader: Raw data load complete! Inserted {inserted_jobs_count} jobs.")
            return True

    except Exception as e:
        logger.critical(f"General error during raw data load: {e}", exc_info=True)
        return False