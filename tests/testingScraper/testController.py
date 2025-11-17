import pytest
from unittest.mock import MagicMock, call
from jobScraper import controller


@pytest.fixture
def mock_dependencies(mocker):
    mock_api_client_instance = MagicMock()
    mocker.patch('job_scraper.controller.ApiClient', return_value=mock_api_client_instance)

    mock_extractor = mocker.patch('job_scraper.controller.extract_jobs_from_page')

    mock_writer_instance = MagicMock()
    mocker.patch('job_scraper.controller.StreamingJsonlWriter', return_value=mock_writer_instance)
    mock_writer_instance.__enter__.return_value = mock_writer_instance

    return {
        "api_client": mock_api_client_instance,
        "extractor": mock_extractor,
        "writer": mock_writer_instance,
    }


def test_run_scraper_happy_path_multiple_pages(mock_dependencies):
    mock_api = mock_dependencies['api_client']
    mock_extractor = mock_dependencies['extractor']
    mock_writer = mock_dependencies['writer']

    def fetch_page_side_effect(page_num):
        if page_num == 1:
            return {"TotalPagesNumber": 3, "TotalSearchResultCount": 30}
        elif page_num == 2:
            return {"ResultList": "data-page-2"}
        elif page_num == 3:
            return {"ResultList": "data-page-3"}
        return None

    mock_api.fetch_page.side_effect = fetch_page_side_effect
    mock_api.base_url = "http://fake.com"

    def extractor_side_effect(data, base_url):
        if data == {"TotalPagesNumber": 3, "TotalSearchResultCount": 30}:
            return [{"title": "Job 1"}]
        elif data == {"ResultList": "data-page-2"}:
            return [{"title": "Job 2"}]
        elif data == {"ResultList": "data-page-3"}:
            return [{"title": "Job 3"}]
        return []

    mock_extractor.side_effect = extractor_side_effect

    controller.run_scraper({})

    assert mock_api.fetch_page.call_count == 3
    mock_api.fetch_page.assert_has_calls([call(1), call(2), call(3)], any_order=True)

    assert mock_extractor.call_count == 3
    assert mock_writer.write_rows.call_count == 3


def test_run_scraper_stops_if_page_1_fails(mock_dependencies):
    mock_api = mock_dependencies['api_client']
    mock_extractor = mock_dependencies['extractor']
    mock_writer = mock_dependencies['writer']

    mock_api.fetch_page.return_value = None

    controller.run_scraper({})

    mock_api.fetch_page.assert_called_once_with(1)
    mock_extractor.assert_not_called()
    mock_writer.write_rows.assert_not_called()


def test_run_scraper_handles_exception_in_thread(mock_dependencies):
    mock_api = mock_dependencies['api_client']
    mock_extractor = mock_dependencies['extractor']
    mock_writer = mock_dependencies['writer']

    def fetch_page_side_effect(page_num):
        if page_num == 1:
            return {"TotalPagesNumber": 3, "TotalSearchResultCount": 30}
        elif page_num == 2:
            raise Exception("Page 2 Failed!")
        elif page_num == 3:
            return {"ResultList": "data-page-3"}
        return None

    mock_api.fetch_page.side_effect = fetch_page_side_effect
    mock_api.base_url = "http://fake.com"

    def extractor_side_effect(data, base_url):
        if data == {"TotalPagesNumber": 3, "TotalSearchResultCount": 30}:
            return [{"title": "Job 1"}]
        elif data == {"ResultList": "data-page-3"}:
            return [{"title": "Job 3"}]
        return []

    mock_extractor.side_effect = extractor_side_effect

    controller.run_scraper({})

    assert mock_api.fetch_page.call_count == 3
    assert mock_extractor.call_count == 2
    assert mock_writer.write_rows.call_count == 2
