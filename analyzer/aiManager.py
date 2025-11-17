import os
import json
import logging
from pathlib import Path
from functools import lru_cache
from typing import List, Optional
from dotenv import load_dotenv



load_dotenv()
import google.generativeai as genai
from pydantic import BaseModel, Field, ValidationError

from . import aiPrompts 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CVAnalysis(BaseModel):
    extracted_skills: List[str] = Field(default_factory=list)
    inferred_experience_level: str = "ללא נסיון"

class ProfileIdentification(BaseModel):
    profile: str = "Unknown Tech Profile"

class GapAnalysis(BaseModel):
    smart_gaps: List[str] = Field(default_factory=list)

class CombinedAIOutput(BaseModel):
    cv_analysis: CVAnalysis
    profile_identification: ProfileIdentification
    gap_analysis: GapAnalysis

class RecommendationOutput(BaseModel):
    opening: str
    gap_analysis_intro: str
    cv_review_title: str
    cv_review_points: List[str]
    closing: str

try:
    API_KEY = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    ai_model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
    text_model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
    logger.info("AI Manager: Gemini 2.5 Flash (JSON mode) successfully initialized.")

except KeyError:
    logger.critical("CRITICAL ERROR: 'GOOGLE_API_KEY' environment variable not set.")
    ai_model = None
    text_model = None
except Exception as e:
    logger.critical(f"AI Manager: Critical error during AI configuration: {e}")
    ai_model = None
    text_model = None

def _call_ai_model(prompt: str, model, is_json: bool = True) -> dict | str:
    if not model:
        logger.error("AI Manager: AI model is not properly initialized.")
        raise ConnectionError("AI service is not properly configured on the server.")
    try:
        response = model.generate_content(prompt)
        
        clean_text = response.text
        if is_json:
            if "```json" in clean_text:
                clean_text = clean_text.split("```json", 1)[1].rsplit("```", 1)[0].strip()
            return json.loads(clean_text)
        
        return clean_text 
        
    except json.JSONDecodeError as e:
        logger.error(f"AI Manager: JSONDecodeError! Cannot parse: {e}")
        logger.error(f"AI Response was: {response.text}")
        raise ValueError(f"AI service returned invalid JSON: {e}")
    except Exception as e:
        logger.error(f"AI Manager: Error in AI call: {e}")
        if 'response' in locals() and hasattr(response, 'prompt_feedback'):
            logger.warning(f"AI Feedback: {response.prompt_feedback}")
        raise e 

def get_structured_cv_analysis(
    cv_text: str, 
    canonical_skills: List[str], 
    canonical_levels: List[str], 
    canonical_profiles: List[str], 
    hint_preferred_profile: Optional[str] = None
) -> CombinedAIOutput:
    
    if not ai_model:
        raise ConnectionError("AI model for JSON is not initialized.")

    logger.info("AI Manager: Sending AI call (Stage 1 - Identification)...")
    
    prompt = aiPrompts.get_initial_cv_analysis_prompt(
        cv_text=cv_text,
        canonical_skills=canonical_skills,
        canonical_levels=canonical_levels,
        user_profiles=canonical_profiles,
        hint_preferred_profile=hint_preferred_profile
    )

    ai_json_output = _call_ai_model(prompt, model=ai_model, is_json=True)
    if not ai_json_output:
        raise ValueError("AI service did not return a JSON response.")
        
    if "error" in ai_json_output:
        logger.warning(f"AI detected invalid input: {ai_json_output['error']}")
        raise ValueError(ai_json_output['error'])

    try:
        analysis_data = CombinedAIOutput.model_validate(ai_json_output)
        return analysis_data
    except ValidationError as e:
        logger.error(f"AI Manager: Invalid JSON from AI! {e}")
        raise ValueError(f"AI service returned an unexpected data structure: {e}")


def get_text_recommendation(
    cv_text: str, 
    user_profile: str, 
    user_skills: List[str], 
    user_level: str, 
    smart_gaps: List[str]
) -> RecommendationOutput:
    
    if not text_model:
        raise ConnectionError("AI model for text (JSON) is not initialized.")
        
    logger.info("AI Manager: Generating personal recommendation (JSON)...")
    
    summary_prompt = aiPrompts.get_summary_prompt(
        cv_text, user_profile, user_skills, user_level, smart_gaps
    )
    
    recommendation_json = _call_ai_model(summary_prompt, model=text_model, is_json=True)
    if not recommendation_json:
        logger.warning("AI Manager: get_text_recommendation did not return JSON.")
        error_data = {
            "opening": "An error occurred while generating the recommendation.",
            "gap_analysis_intro": "",
            "cv_review_title": "Error",
            "cv_review_points": [],
            "closing": ""
        }
        return RecommendationOutput.model_validate(error_data)

    try:
        recommendation_data = RecommendationOutput.model_validate(recommendation_json)
        return recommendation_data
    except ValidationError as e:
        logger.error(f"AI Manager: Invalid JSON from AI (summary)! {e}")
        error_data = {
            "opening": "An error occurred while parsing the recommendation.",
            "gap_analysis_intro": "",
            "cv_review_title": "Parsing Error",
            "cv_review_points": [str(e)],
            "closing": ""
        }
        return RecommendationOutput.model_validate(error_data)