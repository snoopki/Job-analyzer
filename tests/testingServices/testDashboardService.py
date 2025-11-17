import pytest
from api.services import dashboardService
from analyzer import dbQueries


def test_get_dashboard_data_success(mocker):
    fake_skills_data = [
        ('python', 50, 25.0),
        ('react', 30, 15.0)
    ]
    fake_levels_data = [
        {'name': 'Mid', 'count': 100},
        {'name': 'Junior', 'count': 50}
    ]

    mocker.patch(
        'api.services.dashboard_service.db_queries.get_skill_popularity_percentages',
        return_value=fake_skills_data
    )
    mocker.patch(
        'api.services.dashboard_service.db_queries.get_experience_level_distribution',
        return_value=fake_levels_data
    )

    result = dashboardService.get_dashboard_data()

    assert result['total_jobs'] == 150
    assert result['skills'] == fake_skills_data
    assert result['levels'] == fake_levels_data
    assert "total_jobs" in result


def test_get_dashboard_data_handles_db_exception(mocker):
    mocker.patch(
        'api.services.dashboard_service.db_queries.get_skill_popularity_percentages',
        side_effect=Exception("SQL Error")
    )

    with pytest.raises(Exception, match="SQL Error"):
        dashboardService.get_dashboard_data()
