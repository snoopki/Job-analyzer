from analyzer import dbQueries
import logging

logger = logging.getLogger(__name__)

def get_dashboard_data():
    """
    Fetches and processes all data required for the dashboard.
    """
    logger.info("Service: Fetching dashboard data...")
    try:
        skills_data = dbQueries.get_skill_popularity_percentages(top_n=10)
        levels_data = dbQueries.get_experience_level_distribution()
        
        total_jobs = sum([lvl['count'] for lvl in levels_data]) if levels_data else 0
        
        return {
            "skills": skills_data, 
            "levels": levels_data, 
            "total_jobs": total_jobs
        }
    except Exception as e:
        logger.error(f"Service: Error fetching dashboard data: {e}", exc_info=True)
        raise e