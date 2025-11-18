from analyzer import aiManager, dbQueries
import logging
import re

logger = logging.getLogger(__name__)

def normalize(text: str) -> str:
    """ Cleans and normalizes text for simple searching. """
    return re.sub(r'\s+', ' ', text.strip().lower())


def heuristic_persona_detector(
    cv_text: str, 
    canonical_profiles: list, 
    all_skill_keywords: dict
) -> str:
    """
    Dynamic and smart profile detection based on keywords from skill_keywords.json.
    Returns the canonical profile with the highest score.
    """
    text = normalize(cv_text)
    scores = {}

    non_tech_synonyms = all_skill_keywords.get("not a tech profile", [])
    non_tech_hits = sum(1 for kw in non_tech_synonyms if kw in text)
    
    if non_tech_hits >= 1 and not any(kw in text for kw in ["cloud", "azure", "aws", "gcp"]):
        logger.info(f"Heuristic: Detected non-technical profile (found {non_tech_hits} keywords).")
        return "Not a Tech Profile"

    logger.info(f"Heuristic: Scanning {len(canonical_profiles)} canonical profiles...")
    for profile in canonical_profiles:
        if profile == "Not a Tech Profile":
            continue
            
        profile_key = profile.lower()
        synonyms = all_skill_keywords.get(profile_key, [])
        
        score = sum(1 for syn in synonyms if syn in text)
        
        if profile_key in text:
            score += 5 
            
        scores[profile] = score

    if not scores: 
        return "Unknown Tech Profile"

    best_profile = max(scores, key=scores.get)
    
    if scores[best_profile] == 0:
        logger.info("Heuristic: No matching keywords found for any tech profile.")
        return "Unknown Tech Profile"
        
    logger.info(f"Heuristic: Winning profile is '{best_profile}' with score {scores[best_profile]}.")
    return best_profile


def analyze_cv(cv_text: str):
    logger.info("Service: Starting new CV analysis process...")
    try:
        logger.info("Service: Loading canonical data (profiles, skill dictionary, levels)...")
        canonical_profiles = dbQueries.get_all_canonical_profiles()
        skill_keywords_dict = dbQueries.get_skill_keywords_dict() 
        canonical_skills = list(skill_keywords_dict.keys())
        
        level_hierarchy_config = dbQueries.get_level_hierarchy()

        canonical_levels = list(level_hierarchy_config.keys())

        logger.info("Service: Running dynamic profile detection (heuristic)...")
        pre_profile = heuristic_persona_detector(
            cv_text, 
            canonical_profiles, 
            skill_keywords_dict
        )
        logger.info(f"Service: Initial heuristic detection: {pre_profile}")

        logger.info("Service (Stage 1): Sending to AI for profile/skill identification...")
        analysis_data = aiManager.get_structured_cv_analysis(
            cv_text,
            canonical_skills, 
            canonical_levels,
            canonical_profiles, 
            hint_preferred_profile=pre_profile 
        )

        user_skills = analysis_data.cv_analysis.extracted_skills or []
        user_level = analysis_data.cv_analysis.inferred_experience_level or "Unknown"
        user_profile = analysis_data.profile_identification.profile or pre_profile
        logger.info(f"Service: AI identification complete. Profile: {user_profile}, Level: {user_level}")

        if user_profile == "Not a Tech Profile" or pre_profile == "Not a Tech Profile":
            logger.info("Service: Non-technical profile identified, exiting early.")
            recommendation_obj = aiManager.get_text_recommendation(
                cv_text, user_profile, [], user_level, []
            )
            return {
                "recommendation": recommendation_obj,
                "analysis_details": {"cv_skills": [], "market_gaps": []},
                "top_jobs": []
            }

        if user_profile in ("Unknown Tech Profile", None, "") and pre_profile not in ("Unknown Tech Profile", None, ""):
            user_profile = pre_profile
            logger.info(f"Service: AI profile was 'Unknown', falling back to heuristic profile: {user_profile}.")

        logger.info(f"Service (Stage 2): Fetching market skills for {user_profile}...")
        market_skills_for_profile = dbQueries.get_popular_skills_for_profile(
            profile_name=user_profile,
            top_n=20
        )

        if not market_skills_for_profile:
            logger.info("Service: No specific skills found for profile. Fetching global popular skills.")
            market_skills_tuples = dbQueries.get_popular_skills(top_n=20)
            market_skills_for_profile = [s[0] for s in market_skills_tuples] 

        user_skills_set = set([s.lower() for s in user_skills])
        market_skills_set = set([s.lower() for s in market_skills_for_profile])
        smart_gaps = list(market_skills_set - user_skills_set)[:10] 
        logger.info(f"Service (Stage 3): Smart gaps calculated: {smart_gaps}")

        logger.info("Service (Stage 4): Searching for matching jobs...")
        target_level_names = level_hierarchy_config.get(user_level, [user_level]) if user_level else [user_level]
        if not target_level_names or target_level_names == [None]:
            logger.warning(f"Service: User level '{user_level}' not in hierarchy or None. Defaulting to '3-4/5-6'.")
            target_level_names = ['3-4 שנים', '5-6 שנים'] 

        threshold = 0.5
        top_jobs = dbQueries.find_matching_jobs(
            user_skills_list=user_skills,
            target_level_names=target_level_names,
            primary_level_name=user_level,
            threshold=threshold,
            limit=30
        )
        logger.info(f"Service: Found {len(top_jobs)} matching jobs.")

        logger.info("Service (Stage 5): Generating personal recommendation...")
        recommendation_obj = aiManager.get_text_recommendation(
            cv_text, user_profile, user_skills, user_level, smart_gaps
        )

        logger.info("Service (Stage 6): Assembling final response.")
        return {
            "recommendation": recommendation_obj,
            "analysis_details": {
                "cv_skills": user_skills,
                "market_gaps": smart_gaps
            },
            "top_jobs": top_jobs
        }

    except Exception as e:
        logger.critical(f"Service: Critical unhandled error in analyze_cv: {e}", exc_info=True)
        raise e