import pytest
from jobScraper.parser import clean_html, extract_jobs_from_page


def test_clean_html_removes_basic_tags():
    dirty_html = "<p>Hello <b>World</b></p>"
    expected_text = "Hello\nWorld"
    result = clean_html(dirty_html)
    assert result == expected_text


def test_clean_html_handles_br_tags():
    dirty_html = "First line<br>Second line<br/>Third line"
    expected_text = "First line\nSecond line\nThird line"
    result = clean_html(dirty_html)
    assert result == expected_text


def test_clean_html_removes_extra_whitespace():
    dirty_html = "<div>   <p>Line 1</p> </div>   <div>Line 2</div>"
    expected_text = "Line 1\nLine 2"
    result = clean_html(dirty_html)
    assert result == expected_text


def test_clean_html_handles_empty_or_none_input():
    assert clean_html("") == ""
    assert clean_html(None) == ""


@pytest.fixture
def mock_api_data():
    return {
        "ResultList": [
            {
                "JobContent": {
                    "Name": "Software Engineer",
                    "Description": "<p>We are hiring</p>",
                    "Requirements": "<b>Python</b> skills",
                    "Experience": {"NameInHebrew": "1-2 שנים"},
                    "Addresses": [{"City": "Tel Aviv"}],
                    "Regions": []
                },
                "Company": {"CompanyDisplayName": "Google"},
                "JobInfo": {"Link": "/job/123"}
            },
            {
                "JobContent": {
                    "Name": "Frontend Developer",
                    "Description": "React job",
                    "Requirements": "CSS",
                    "Experience": {"NameInHebrew": "3-4 שנים"},
                    "Addresses": [{"City": "Haifa"}, {"City": "Tel Aviv"}],
                    "Regions": []
                },
                "Company": {"CompanyDisplayName": "Facebook"},
                "JobInfo": {"Link": "/job/456"}
            }
        ]
    }


def test_extract_jobs_basic_parsing(mock_api_data):
    base_url = "https://example.com"
    jobs = extract_jobs_from_page(mock_api_data, base_url)

    assert len(jobs) == 2

    assert jobs[0]['title'] == "Software Engineer"
    assert jobs[0]['company'] == "Google"
    assert jobs[0]['link'] == "https://example.com/job/123"
    assert jobs[0]['experience'] == "1-2 שנים"
    assert jobs[0]['locations'] == ["Tel Aviv"]

    assert "תיאור משרה:" in jobs[0]['description']
    assert "We are hiring" in jobs[0]['description']
    assert "דרישות:" in jobs[0]['description']
    assert "Python" in jobs[0]['description']
    assert "skills" in jobs[0]['description']

    assert jobs[1]['title'] == "Frontend Developer"
    assert jobs[1]['locations'] == ["Haifa", "Tel Aviv"]
