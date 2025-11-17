import pytest
from unittest.mock import MagicMock
from api.services import analysisService
from analyzer import aiManager, dbQueries


def test_normalize():
    assert analysisService.normalize("  Hello World  ") == "hello world"
    assert analysisService.normalize("Test\nWith\nNewlines") == "test with newlines"
    assert analysisService.normalize("Test  With   Spaces") == "test with spaces"


@pytest.fixture
def mock_dictionaries():
    canonical_profiles = [
        "Full Stack Developer",
        "Data Engineer",
        "DevOps Engineer",
        "Not a Tech Profile",
        "Unknown Tech Profile"
    ]

    all_skill_keywords = {
        "full stack developer": ["full stack developer", "fullstack", "react", "node.js"],
        "data engineer": ["data engineer", "etl", "spark", "data pipeline"],
        "devops engineer": ["devops engineer", "ci/cd", "kubernetes", "jenkins"],
        "not a tech profile": ["sales", "marketing", "teacher"]
    }
    return canonical_profiles, all_skill_keywords


def test_detector_finds_by_synonym(mock_dictionaries):
    profiles, keywords = mock_dictionaries
    cv_text = "I love building ETL pipelines with Python and Spark."
    result = analysisService.heuristic_persona_detector(cv_text, profiles, keywords)
    assert result == "Data Engineer"


def test_detector_gives_bonus_for_exact_match(mock_dictionaries):
    profiles, keywords = mock_dictionaries
    cv_text = "I am a Data Engineer who also knows react and node.js"
    result = analysisService.heuristic_persona_detector(cv_text, profiles, keywords)
    assert result == "Data Engineer"


def test_detector_finds_non_tech_profile(mock_dictionaries):
    profiles, keywords = mock_dictionaries
    cv_text = "I worked in sales for 5 years."
    result = analysisService.heuristic_persona_detector(cv_text, profiles, keywords)
    assert result == "Not a Tech Profile"


def test_detector_ignores_non_tech_if_cloud_exists(mock_dictionaries):
    profiles, keywords = mock_dictionaries
    cv_text = "I worked in sales but now I am learning AWS and kubernetes."
    result = analysisService.heuristic_persona_detector(cv_text, profiles, keywords)
    assert result == "DevOps Engineer"


def test_detector_handles_unknown_profile(mock_dictionaries):
    profiles, keywords = mock_dictionaries
    cv_text = "I am a C++ programmer."
    result = analysisService.heuristic_persona_detector(cv_text, profiles, keywords)
    assert result == "Unknown Tech Profile"


def test_analyze_cv_full_pipeline_happy_path(mocker):
    fake_profiles = ["Full Stack Developer", "Data Engineer"]
    fake_skill_dict = {
        "full stack developer": ["react", "node.js"],
        "python": ["python"],
        "aws": ["aws"],
        "c#": ["c#"]
    }
    fake_market_skills = ["react", "node.js", "aws", "c#"]
    fake_jobs = [{"title": "Full Stack Job", "match_percentage": 80}]

    mock_ai_analysis = MagicMock()
    mock_ai_analysis.cv_analysis.extracted_skills = ["python", "react"]
    mock_ai_analysis.cv_analysis.inferred_experience_level = "1-2 שנים"
    mock_ai_analysis.profile_identification.profile = "Full Stack Developer"

    mock_ai_recommendation = MagicMock()
    mock_ai_recommendation.opening = "זוהי המלצה."

    mocker.patch('analyzer.db_queries.get_all_canonical_profiles', return_value=fake_profiles)
    mocker.patch('analyzer.db_queries.get_skill_keywords_dict', return_value=fake_skill_dict)
    mocker.patch('analyzer.db_queries.get_popular_skills_for_profile', return_value=fake_market_skills)
    mocker.patch('analyzer.db_queries.find_matching_jobs', return_value=fake_jobs)

    mocker.patch('analyzer.aiManager.get_structured_cv_analysis', return_value=mock_ai_analysis)
    mocker.patch('analyzer.aiManager.get_text_recommendation', return_value=mock_ai_recommendation)

    mocker.patch(
        'api.services.analysis_service.heuristic_persona_detector',
        return_value="Full Stack Developer"
    )

    result = analysisService.analyze_cv("My CV text...")

    expected_gaps = {"node.js", "aws", "c#"}
    assert set(result['analysis_details']['market_gaps']) == expected_gaps

    assert result['analysis_details']['cv_skills'] == ["python", "react"]
    assert result['top_jobs'][0]['title'] == "Full Stack Job"
    assert result['recommendation'].opening == "זוהי המלצה."
