import pytest
from unittest.mock import MagicMock


from analyzer.aiManager import (
    CombinedAIOutput, 
    RecommendationOutput, 
    _call_ai_model, 
    get_structured_cv_analysis,
    get_text_recommendation
)

def test_call_ai_model_cleans_json_markdown():
    dirty_json_string = "```json\n{ \"skill\": \"python\" }\n```"
    expected_dict = {"skill": "python"}
    
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = dirty_json_string
    mock_model.generate_content.return_value = mock_response

    result = _call_ai_model("test prompt", model=mock_model, is_json=True)

    assert result == expected_dict
    mock_model.generate_content.assert_called_once_with("test prompt")


def test_get_structured_cv_analysis_success(mocker):
    fake_ai_response = {
        "cv_analysis": {
            "extracted_skills": ["python", "react"],
            "inferred_experience_level": "1-2 שנים"
        },
        "profile_identification": {
            "profile": "Full Stack Developer"
        },
        "gap_analysis": {
            "smart_gaps": []
        }
    }
    mocker.patch('analyzer.aiManager.ai_model', MagicMock())
    mocker.patch(
        'analyzer.aiManager._call_ai_model', 
        return_value=fake_ai_response
    )
    mocker.patch('analyzer.ai_prompts.get_initial_cv_analysis_prompt', return_value="fake prompt")

    result = get_structured_cv_analysis(
        "dummy cv text", ["python", "react"], ["1-2 שנים"], ["Full Stack Developer"]
    )
    assert isinstance(result, CombinedAIOutput)
    assert result.cv_analysis.extracted_skills == ["python", "react"]


def test_get_structured_cv_analysis_validation_error(mocker):
    fake_bad_response = {
        "cv_analysis": {
            "extracted_skills": ["python"],
            "inferred_experience_level": "1-2 שנים"
        },
        "profile_identification": "THIS SHOULD BE A DICT",
        "gap_analysis": {"smart_gaps": []}
    }
    
    mocker.patch('analyzer.aiManager.ai_model', MagicMock())
    mocker.patch(
        'analyzer.aiManager._call_ai_model', 
        return_value=fake_bad_response
    )
    mocker.patch('analyzer.ai_prompts.get_initial_cv_analysis_prompt', return_value="fake prompt")


    with pytest.raises(ValueError, match="שירות ה-AI החזיר מבנה נתונים שגוי"):
        get_structured_cv_analysis(
            "dummy cv text", [], [], []
        )


def test_get_text_recommendation_skips_ai_for_non_tech(mocker):    
    expected_non_tech_json = {
        "opening": "שלום, כאן יועץ הקריירה מבוסס הנתונים של Drushim IL. ניתחנו את קורות החיים שלך וזיהינו שהם מתארים פרופיל מקצועי שאינו בתחום ההייטק.",
        "gap_analysis_intro": "המערכת שלנו ממוקדת בפרופילים טכטולוגיים, ולכן אין ניתוח פערים רלוונטי במקרה זה.",
        "cv_review_title": "המלצה",
        "cv_review_points": [
            "**התאמה כללית:** קורות החיים אינם טכנולוגיים, ולכן מומלץ לחפש משרות בתחומים שאינם דורשים ידע בפיתוח או טכטולוגיה."
        ],
        "closing": "אנו מאחלים לך הצלחה רבה בכל נתיב הקריירה שתבחר."
    }
    
    mocker.patch('analyzer.aiManager.text_model', MagicMock())
    mocker.patch(
        'analyzer.aiManager._call_ai_model', 
        return_value=expected_non_tech_json
    )
    mocker.patch('analyzer.ai_prompts.get_summary_prompt', return_value="fake non-tech prompt")

    profile = "Not a Tech Profile"
    
    result = get_text_recommendation(
        "cv text", profile, [], "1-2 שנים", []
    )

    assert isinstance(result, RecommendationOutput)
    assert "פרופיל מקצועי שאינו בתחום ההייטק" in result.opening
    assert result.cv_review_title == "המלצה"