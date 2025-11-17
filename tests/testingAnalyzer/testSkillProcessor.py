import pytest
from analyzer.skillProcessor import extract_skills_from_text, _load_skill_keywords, _get_compiled_skill_engine


@pytest.fixture
def fake_skill_keywords():
    return {
        "python": ["python", "py"],
        "react": ["react", "react.js"],
        "c++": ["c++", "cpp"],
        "c#": ["c#", "c-sharp"],
        "c": ["c"],
        "docker": ["docker"],
    }


@pytest.fixture(autouse=True)
def mock_file_loading(mocker, fake_skill_keywords):
    mocker.patch(
        'analyzer.skillProcessor._load_skill_keywords',
        return_value=fake_skill_keywords
    )

    _load_skill_keywords.cache_clear()
    _get_compiled_skill_engine.cache_clear()


def test_extract_skills_basic():
    text = "I am a programmer who knows python and docker."
    job_id = 1
    _id, skills = extract_skills_from_text(job_id, text)
    assert _id == job_id
    assert set(skills) == {"python", "docker"}


def test_extract_skills_synonyms_and_case():
    text = "I love PyThOn and also react.js framework."
    job_id = 2
    _id, skills = extract_skills_from_text(job_id, text)
    assert set(skills) == {"python", "react"}


def test_extract_skills_whole_word_matching():
    text = "I am a happy programmer. I need a react-or."
    job_id = 3
    _id, skills = extract_skills_from_text(job_id, text)
    assert "python" not in skills
    assert "react" not in skills
    assert len(skills) == 0


def test_extract_skills_special_cases():
    text = "I know c, c++, and c# (or c-sharp). I also use cpp."
    job_id = 4
    _id, skills = extract_skills_from_text(job_id, text)
    assert set(skills) == {"c", "c++", "c#"}


def test_extract_skills_empty_input():
    text = ""
    job_id = 5
    _id, skills = extract_skills_from_text(job_id, text)
    assert len(skills) == 0
