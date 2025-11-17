import pytest
import requests
from unittest.mock import MagicMock
from jobScraper.api import ApiClient
from jobSearchConfig import BASE_URL, MAIN_CATEGORIES, build_api_params


def test_build_api_params_page_number():
    params = build_api_params(page=5)
    assert params['page'] == 5


def test_build_api_params_categories():
    params = build_api_params(
        main_category_key="hitech_software",
        subcategories_keys=["backend", "devops"]
    )
    assert params['subcat'] == "616-491"
    assert 'catdir' not in params


def test_build_api_params_experience_none():
    params = build_api_params(experience_key=None)
    assert 'experience' not in params


@pytest.fixture
def api_client():
    mock_search_config = {
        "main_category": "hitech_software",
        "roles": ["backend"],
        "experience": "all",
        "keyword": None
    }
    return ApiClient(mock_search_config)


def test_fetch_page_success(mocker, api_client):
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"TotalPagesNumber": 10}
    fake_response.raise_for_status.return_value = None

    mocker.patch('requests.get', return_value=fake_response)

    data = api_client.fetch_page(1)
    assert data == {"TotalPagesNumber": 10}


def test_fetch_page_http_error_404(mocker, api_client):
    fake_response = MagicMock()
    fake_response.status_code = 404
    fake_response.raise_for_status.side_effect = requests.exceptions.RequestException

    mocker.patch('requests.get', return_value=fake_response)

    data = api_client.fetch_page(1)
    assert data is None


def test_fetch_page_retries_on_timeout_then_succeeds(mocker, api_client):
    success_response = MagicMock()
    success_response.status_code = 200
    success_response.json.return_value = {"TotalPagesNumber": 10}
    success_response.raise_for_status.return_value = None

    mocker.patch('requests.get', side_effect=[
        requests.exceptions.Timeout("Connection timed out"),
        success_response
    ])
    mocker.patch('time.sleep')

    data = api_client.fetch_page(1, retries=3)

    assert data == {"TotalPagesNumber": 10}
