import json
from typing import List, Optional

def get_initial_cv_analysis_prompt(
    cv_text: str, 
    canonical_skills: List[str], 
    canonical_levels: List[str], 
    user_profiles: List[str], 
    hint_preferred_profile: Optional[str] = None
) -> str:
    """
    Generates the Stage 1 prompt for initial CV data extraction.
    This prompt instructs the AI to extract skills, level, and profile,
    but to skip gap analysis.
    """

    hint_section = ""
    if hint_preferred_profile and hint_preferred_profile not in ["Unknown Tech Profile", "Not a Tech Profile"]:
        hint_section = f"""
        ---
        Profile Hint
        ---
        A preliminary analysis suggests the user's profile is likely: **{hint_preferred_profile}**.
        Use this hint to improve the accuracy of your profile selection in Part 2.
        If the CV text strongly contradicts this hint, you may override it, but give it strong consideration.
        """

    return f"""
    You are an expert tech career analysis system.
    Your task is to analyze a resume and extract 3 key pieces of information.
    You must return a single JSON object with 3 top-level keys: "cv_analysis", "profile_identification".

    {hint_section}

    ---
    Part 1: CV Analysis (cv_analysis)
    ---
    Analyze the following resume:
    {cv_text}

    Mandatory Rules for Part 1:
    1.  For 'extracted_skills', return *only* canonical names from the following list: {canonical_skills}
    2.  If you find a synonym (like 'react.js'), return the corresponding canonical name (e.g., 'react').
    3.  For 'inferred_experience_level', select *only* one of the following options: {canonical_levels}.
    3.5. When returning the selected level, return the exact string *without* the surrounding quotes (e.g., return "1-2 שנים", NOT "'1-2 שנים'").
    4.  **Crucial Rule for Experience:** You MUST select 'ללא נסיון' (No experience) UNLESS the CV text contains clear evidence of professional, paid work experience (a job title, company name, and time frame) relevant to the tech industry. Do NOT count university projects, bootcamps, or personal projects as 'experience'. If no clear job is listed, the level MUST be 'ללא נסיון'.

    ---
    Part 2: Profile Identification (profile_identification)
    ---
    Based on the skills extracted in Part 1, select the *single* primary profile that best describes the user from the following list:
    {user_profiles}

    Mandatory Rules for Part 2:
    5.  **Fallback Rule:** If the CV has very few tech skills or seems entirely non-technical (e.g., 'Baker', 'Lawyer'), you MUST select the profile: **'Not a Tech Profile'**.
        (This 'Not a Tech Profile' *must* exist in the user_profiles list you provide).
        Do NOT try to force a tech profile like 'Software Developer'.

    ---
    Part 3: Gap Analysis (gap_analysis)
    ---
    
    ---
    Final JSON Output (in this exact format):
    ---
    {{
      "cv_analysis": {{
        "extracted_skills": ["skill1_canonical", "skill2_canonical", ...],
        "inferred_experience_level": "canonical-level-name"
      }},
      "profile_identification": {{
        "profile": "selected-profile-name"
      }},
      "gap_analysis": {{
        "smart_gaps": [] 
      }}
    }}
    """

def get_summary_prompt(cv_text: str, user_profile: str, cv_skills: list, user_level: str, smart_gaps: list) -> str:
    """
    Generates a structured, professional summary in Hebrew for the user.
    Handles both tech and non-tech profiles.
    """

    non_tech_profile_name = "Not a Tech Profile"
    unknown_profile_name = "Unknown Tech Profile" 

    if user_profile == non_tech_profile_name:
        non_tech_response = {
            "opening": "שלום, כאן יועץ הקריירה מבוסס הנתונים של Drushim IL. ניתחנו את קורות החיים שלך וזיהינו שהם מתארים פרופיל מקצועי שאינו בתחום ההייטק.",
            "gap_analysis_intro": "המערכת שלנו ממוקדת בפרופילים טכנולוגיים, ולכן אין ניתוח פערים רלוונטי במקרה זה.",
            "cv_review_title": "המלצה",
            "cv_review_points": [
                "**התאמה כללית:** קורות החיים אינם טכנולוגיים, ולכן מומלץ לחפש משרות בתחומים שאינם דורשים ידע בפיתוח או טכנולוגיה."
            ],
            "closing": "אנו מאחלים לך הצלחה רבה בכל נתיב הקריירה שתבחר."
        }
        return f"""
You are an AI assistant. The user's profile was identified as non-technical.
Return exactly the following JSON object — nothing else, no explanations:

{json.dumps(non_tech_response, ensure_ascii=False, indent=2)}
"""

    if user_profile == unknown_profile_name:
        unknown_response = {
            "opening": f"שלום, כאן יועץ הקריירה מבוסס הנתונים של Drushim IL. ניתחנו את קורות החיים שלך (ניסיון שזוהה: {user_level}).",
            "gap_analysis_intro": "לא הצלחנו לזהות באופן אוטומטי פרופיל טכנולוגי ברור (כמו 'DevOps' או 'Data Analyst') מקורות החיים.",
            "cv_review_title": "המלצות לשיפור",
            "cv_review_points": [
                "**חידוד פרופיל:** אנא ודא שכותרת קורות החיים שלך (Title) וקטע הסיכום (Personal Profile) ברורים וממוקדים לתפקיד שאליו אתה מכוון.",
                "**מילות מפתח:** ודא שהכישורים והטכנולוגיות המרכזיות שלך מופיעים באופן בולט בקורות החיים."
            ],
            "closing": "לאחר חידוד הפרופיל, נשמח לנסות לנתח שוב."
        }
        return f"""
You are an AI assistant. The user's profile could not be identified.
Your *only* task is to return the following JSON object exactly as written, without any changes or extra text.
        
{json.dumps(unknown_response, ensure_ascii=False, indent=2)}
"""

    return f"""
You are an expert AI Career Advisor for the Israeli tech market.
Your mission: write a truthful, professional JSON analysis in **Hebrew** (skill names may remain in English).

You have the following data:
- Profile: {user_profile}
- Skills: {cv_skills}
- Experience Level: {user_level}
- Gaps: {smart_gaps}
- Raw CV: {cv_text}

Use a confident, practical, data-driven tone. No fluff.

Return JSON with the following structure:
{{
  "opening": "פתיח מקצועי המציג את הפרופיל שזוהה ({user_profile}), את רמת הניסיון ({user_level}), ואת נקודות החוזקה העיקריות על בסיס {cv_skills}.",
  "gap_analysis_intro": "הצג בצורה ברורה את הפערים ({smart_gaps}) ולמה חשוב להשלים אותם, בהקשר ישיר לתפקיד {user_profile}.",
  "cv_review_title": "ניתוח קורות החיים והמלצות",
  "cv_review_points": [
    "**סיכום אישי (About Me):** הערך את מיקוד הסיכום. **אם הוא ממוקד ואיכותי, ציין זאת כנקודת חוזק.** אם הוא גנרי מדי (למשל, 'גם פרונט וגם בק') או לא תואם לפרופיל שזוהה, הצע למקד אותו.",
    "**פרויקטים/ניסיון:** הערך את תיאור הפרויקטים. **אם הם מרשימים ומתארים הישגים בצורה טובה, ציין זאת.** אם חסר פירוט טכני, הצע להוסיף הישגים מדידים או טכנולוגיות ספציפיות ({cv_skills}) שהשתמשת בהן.",
    "**רשימת כישורים:** בדוק את רשימת הכישורים. **אם היא מאורגנת היטב ומסונכרנת עם הפרויקטים, ציין שזה מצוין.** אם היא לא מסונכרנת (למשל, כישורים מהפרויקטים חסרים ברשימה), הצע לסנכרן אותה."
  ],
  "closing": "סיים בפסקת סיכום מעודדת ומקצועית עם המלצה להמשך הדרך."
}}
"""