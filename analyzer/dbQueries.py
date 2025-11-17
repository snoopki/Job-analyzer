import sqlite3
import logging
from .dbCore import get_db_connection, get_or_create_id
from functools import lru_cache
import json
from pathlib import Path

logger = logging.getLogger(__name__)

def get_jobs_to_process():
    """ 
    Fetches *all* jobs from the DB for skill processing.
    """
    jobs = []
    try:
        with get_db_connection() as conn:
            if conn is None: 
                logger.error("DB Queries: Could not get DB connection in get_jobs_to_process.")
                return []
            cursor = conn.cursor()
            cursor.execute("SELECT job_id, description FROM jobs")
            jobs = cursor.fetchall()
            logger.info(f"DB Queries: Found {len(jobs)} jobs to process for skills.")
    except sqlite3.Error as e:
        logger.error(f"DB Queries: Error fetching jobs to process: {e}", exc_info=True)
    return jobs

def save_processed_skills(processed_results: dict):
    """
    Saves the processed skills (from skillProcessor) into the DB.
    """
    if not processed_results:
        logger.warning("DB Queries: No processed skills received to save (processed_results is empty).")
        return False

    logger.info(f"DB Queries: Starting to save processed skills for {len(processed_results)} jobs...")
    all_job_skills_to_insert = []
    skill_cache = {} 

    try:
        with get_db_connection() as conn:
            if conn is None: 
                logger.error("DB Queries: Could not get DB connection in save_processed_skills.")
                return False
            cursor = conn.cursor()

            logger.info("DB Queries: Clearing old skill links (DELETE FROM job_skills)...")
            cursor.execute("DELETE FROM job_skills;")

            for job_id, skills_list in processed_results.items():
                if not skills_list: continue

                for skill_name in skills_list:
                    if not skill_name: continue
                    
                    skill_id = get_or_create_id(cursor, "skills", "skill", skill_name, skill_cache)
                    
                    if skill_id:
                        all_job_skills_to_insert.append((job_id, skill_id))

            if all_job_skills_to_insert:
                logger.info(f"DB Queries: Inserting {len(all_job_skills_to_insert)} skill links into job_skills table...")
                cursor.executemany("INSERT OR IGNORE INTO job_skills (job_id, skill_id) VALUES (?, ?)", all_job_skills_to_insert)
            
            conn.commit()
            logger.info("DB Queries: Saving processed skills complete!")
            return True

    except Exception as e:
        logger.critical(f"DB Queries: Critical error while saving processed skills: {e}", exc_info=True)
        return False

@lru_cache(maxsize=1)
def get_popular_skills(top_n=20):
    """
    Fetches the top N most popular skills.
    """
    query = """
        SELECT 
            s.skill_name, 
            COUNT(js.job_id) AS job_count
        FROM skills AS s
        JOIN job_skills AS js ON s.skill_id = js.skill_id
        GROUP BY s.skill_name
        ORDER BY job_count DESC
        LIMIT ?
    """
    
    results = []
    try:
        with get_db_connection() as conn:
            if conn is None: 
                logger.error("DB Queries: Could not get DB connection in get_popular_skills.")
                return []
            cursor = conn.cursor()
            cursor.execute(query, (top_n,))
            results = cursor.fetchall()
            logger.info(f"DB Queries: Fetched {len(results)} popular skills (from DB, not cache).")
    except sqlite3.Error as e:
        logger.error(f"DB Queries: Error fetching popular skills: {e}", exc_info=True)
    
    return results

def find_matching_jobs(
    user_skills_list: list, 
    target_level_names: list, 
    primary_level_name: str, 
    threshold: float = 0.0, 
    limit: int = 30
):
    """
    Finds the most relevant matching jobs.
    """
    
    try:
        with get_db_connection() as conn:
            if conn is None: 
                logger.error("DB Queries: Could not get DB connection in find_matching_jobs.")
                return []
            cursor = conn.cursor()

            if not user_skills_list: 
                logger.warning("DB Queries: find_matching_jobs received an empty skill list.")
                return [] 
            
            skill_placeholders = ','.join(['?'] * len(user_skills_list))
            cursor.execute(f"SELECT skill_id FROM skills WHERE skill_name IN ({skill_placeholders})", user_skills_list)
            user_skill_ids = [row[0] for row in cursor.fetchall()]
            if not user_skill_ids: 
                logger.warning(f"DB Queries: User skills {user_skills_list} not found in DB.")
                return []

            level_placeholders = ','.join(['?'] * len(target_level_names))
            cursor.execute(f"SELECT level_id, level_name FROM experience_levels WHERE level_name IN ({level_placeholders})", target_level_names)
            level_map = {name: id for id, name in cursor.fetchall()}
            
            target_level_ids = list(level_map.values())
            primary_level_id = level_map.get(primary_level_name) 

            logger.debug(f"DB Queries: Searching for level IDs for: {target_level_names}")
            logger.debug(f"DB Queries: IDs found: {level_map}")

            if not target_level_ids or primary_level_id is None:
                if not level_map.get(primary_level_name):
                    logger.error(f"DB Queries: Error! Primary level '{primary_level_name}' not found in DB.")
                    return []

            skill_id_placeholders = ','.join(['?'] * len(user_skill_ids))
            level_id_placeholders = ','.join(['?'] * len(target_level_ids))

            query = f"""
            WITH JobMatchStats AS (
                SELECT
                    js.job_id, j.title, j.link, j.level_id, j.company_id,
                    COUNT(js.skill_id) AS total_skills_required,
                    SUM(CASE WHEN js.skill_id IN ({skill_id_placeholders}) THEN 1 ELSE 0 END) AS user_matched_skills
                FROM job_skills AS js
                JOIN jobs AS j ON js.job_id = j.job_id
                WHERE j.level_id IN ({level_id_placeholders})
                GROUP BY js.job_id, j.title, j.link, j.level_id, j.company_id
            ),
            JobPenalizedStats AS (
                SELECT
                    jms.job_id, jms.title, jms.link, el.level_name, c.company_name,
                    CASE 
                        WHEN jms.level_id = ? THEN (CAST(jms.user_matched_skills AS REAL) / jms.total_skills_required)
                        ELSE (CAST(jms.user_matched_skills AS REAL) / jms.total_skills_required) - 0.25 
                    END AS match_percentage
                FROM JobMatchStats AS jms
                JOIN experience_levels AS el ON jms.level_id = el.level_id
                JOIN companies AS c ON jms.company_id = c.company_id
            )
            SELECT 
                jps.job_id, jps.title, jps.link, jps.level_name, jps.match_percentage, jps.company_name
            FROM JobPenalizedStats AS jps
            WHERE jps.match_percentage >= ?
            ORDER BY
                jps.match_percentage DESC
            LIMIT ?;
            """

            params = user_skill_ids + target_level_ids + [primary_level_id] + [threshold, limit]
            
            cursor.execute(query, params)
            rows = cursor.fetchall()

            results = []
            for row in rows:
                results.append({
                    "title": row[1],
                    "link": row[2],
                    "level": row[3], 
                    "match_percentage": int(row[4] * 100),
                    "company": row[5] 
                })
            
            logger.info(f"DB Queries: Found {len(results)} matching jobs.")
            return results

    except sqlite3.Error as e:
        logger.error(f"DB Queries: Critical error in find_matching_jobs: {e}", exc_info=True)
        return []

def get_experience_level_distribution():
    """
    Counts the number of jobs for each experience level (for dashboard pie chart).
    """
    query = """
        SELECT 
            el.level_name AS name, 
            COUNT(j.job_id) AS count
        FROM jobs AS j
        JOIN experience_levels AS el ON j.level_id = el.level_id
        GROUP BY el.level_name
        ORDER BY count DESC;
    """
    
    results = []
    try:
        with get_db_connection() as conn:
            if conn is None: 
                logger.error("DB Queries: Could not get DB connection in get_experience_level_distribution.")
                return []
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()] 
            logger.debug(f"DB Queries: Fetched experience level distribution: {results}")
    except sqlite3.Error as e:
        logger.error(f"DB Queries: Error fetching level distribution: {e}", exc_info=True)
    
    return results

def get_skill_popularity_percentages(top_n=20):
    """
    Returns a list of skills + job count + percentage of total jobs.
    """
    query = """
        WITH total_jobs AS (
            SELECT COUNT(*) AS total_count FROM jobs
        )
        SELECT 
            s.skill_name AS skill,
            COUNT(js.job_id) AS job_count,
            ROUND((COUNT(js.job_id) * 100.0 / tj.total_count), 1) AS percentage
        FROM skills AS s
        JOIN job_skills AS js ON s.skill_id = js.skill_id
        CROSS JOIN total_jobs AS tj
        GROUP BY s.skill_name, tj.total_count
        ORDER BY job_count DESC
        LIMIT ?;
    """

    try:
        with get_db_connection() as conn:
            if conn is None:
                logger.error("DB Queries: Could not get DB connection in get_skill_popularity_percentages.")
                return []
            cursor = conn.cursor()
            cursor.execute(query, (top_n,))
            results = cursor.fetchall()
            logger.debug(f"DB Queries: Fetched {len(results)} skills with percentages: {results}")
            return results
    except sqlite3.Error as e:
        logger.error(f"DB Queries: Error fetching skills with percentages: {e}", exc_info=True)
        return []

@lru_cache(maxsize=128)
def get_popular_skills_for_profile(profile_name: str, top_n: int = 20):
    """
    Fetches the most popular skills for a specific profile.
    Tries 3 methods: by profile column, by title LIKE, by keywords.
    """
    if not profile_name:
        return []

    try:
        with get_db_connection() as conn:
            if conn is None: 
                logger.error("DB Queries: Could not get DB connection in get_popular_skills_for_profile.")
                return []
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    SELECT s.skill_name, COUNT(js.job_id) AS job_count
                    FROM skills s
                    JOIN job_skills js ON s.skill_id = js.skill_id
                    JOIN jobs j ON js.job_id = j.job_id
                    WHERE LOWER(j.profile_name) = LOWER(?)
                    GROUP BY s.skill_name
                    ORDER BY job_count DESC
                    LIMIT ?
                """, (profile_name, top_n))
                rows = cursor.fetchall()
                if rows:
                    logger.info(f"DB Queries: Found {len(rows)} skills for profile '{profile_name}' (by column).")
                    return [r[0] for r in rows]
            except sqlite3.Error:
                pass

            cursor.execute("""
                SELECT s.skill_name, COUNT(js.job_id) AS job_count
                FROM skills s
                JOIN job_skills js ON s.skill_id = js.skill_id
                JOIN jobs j ON js.job_id = j.job_id
                WHERE LOWER(j.title) LIKE LOWER(?)
                GROUP BY s.skill_name
                ORDER BY job_count DESC
                LIMIT ?
            """, (f"%{profile_name}%", top_n))
            rows = cursor.fetchall()
            if rows:
                logger.info(f"DB Queries: Found {len(rows)} skills for profile '{profile_name}' (by title LIKE).")
                return [r[0] for r in rows]

            keywords = profile_name.lower().split()
            placeholders = " OR ".join(["LOWER(j.title) LIKE ?"] * len(keywords))
            params = [f"%{kw}%" for kw in keywords] + [top_n]
            cursor.execute(f"""
                SELECT s.skill_name, COUNT(js.job_id) AS job_count
                FROM skills s
                JOIN job_skills js ON s.skill_id = js.skill_id
                JOIN jobs j ON js.job_id = j.job_id
                WHERE {placeholders}
                GROUP BY s.skill_name
                ORDER BY job_count DESC
                LIMIT ?
            """, params)
            rows = cursor.fetchall()
            if rows:
                logger.info(f"DB Queries: Found {len(rows)} skills for profile '{profile_name}' (by keywords).")
                return [r[0] for r in rows]

    except sqlite3.Error as e:
        logger.error(f"DB Queries: Error fetching skills by profile ({profile_name}): {e}", exc_info=True)

    logger.warning(f"DB Queries: No skills found at all for profile '{profile_name}'.")
    return []

def get_all_canonical_profiles():
    """Load canonical profiles from JSON file."""
    path = Path(__file__).parent / "ProfileConfig.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        profiles = data.get("profiles", [])
        logger.info(f"DB Queries: Loaded {len(profiles)} canonical profiles from JSON.")
        return profiles
    except Exception as e:
        logger.critical(f"CRITICAL ERROR: Failed to load ProfileConfig.json: {e}", exc_info=True)
        return []
    
@lru_cache(maxsize=1)
def get_level_hierarchy():
    """Loads the level hierarchy from ProfileConfig.json file."""
    path = Path(__file__).parent / "ProfileConfig.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        hierarchy = data.get("level_hierarchy", {})
        if not hierarchy:
            logger.warning("DB Queries: 'level_hierarchy' key not found or empty in ProfileConfig.json.")
        else:
            logger.info("DB Queries: Loaded level hierarchy from ProfileConfig.json.")
        return hierarchy
    except Exception as e:
        logger.critical(f"CRITICAL ERROR: Failed to load ProfileConfig.json: {e}", exc_info=True)
        return {}

@lru_cache(maxsize=1) 
def get_all_canonical_skills():
    """Load canonical skills map from JSON file and return its keys."""
    
    path = Path(__file__).parent / "skill_keywords.json"
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        skill_list = list(data.keys())
        logger.info(f"DB Queries: Loaded {len(skill_list)} canonical skills (keys) from skill_keywords.json.")
        return skill_list
        
    except FileNotFoundError:
        logger.critical(f"CRITICAL ERROR: File 'skill_keywords.json' not found at path: {path}")
        return []
    except Exception as e:
        logger.critical(f"CRITICAL ERROR: Failed to load skill_keywords.json: {e}", exc_info=True)
        return []

@lru_cache(maxsize=1)
def get_skill_keywords_dict():
    """Loads the full skill keywords dictionary (with synonyms)."""
    path = Path(__file__).parent / "skill_keywords.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"DB Queries: Loaded full 'skill_keywords.json' dictionary with {len(data)} keys.")
        return data
    except Exception as e:
        logger.critical(f"CRITICAL ERROR: Failed to load skill_keywords.json: {e}", exc_info=True)
        return {}