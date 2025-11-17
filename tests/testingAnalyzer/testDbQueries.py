import pytest
import sqlite3
from analyzer import dbQueries
from analyzer.dbLoader import create_schema

@pytest.fixture(autouse=True)
def clear_lru_caches():
    yield
    
    dbQueries.get_popular_skills.cache_clear()
    dbQueries.get_popular_skills_for_profile.cache_clear()
    dbQueries.get_all_canonical_skills.cache_clear()
    dbQueries.get_skill_keywords_dict.cache_clear()
    dbQueries.get_level_hierarchy.cache_clear()
    dbQueries.get_all_canonical_profiles.cache_clear()


@pytest.fixture
def mock_db(mocker):
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    
    create_schema(cursor)
    
    cursor.executemany("INSERT INTO companies (company_name) VALUES (?)", 
        [('Google',), ('Facebook',), ('TestCo',)])
    cursor.executemany("INSERT INTO experience_levels (level_name) VALUES (?)", 
        [('Junior',), ('Mid',), ('Senior',)])
    
    conn.commit()
    
    mocker.patch('analyzer.db_queries.get_db_connection', return_value=conn)
    
    yield conn
    
    conn.close()


def test_save_and_get_skills(mock_db):
    cursor = mock_db.cursor()
    cursor.executemany("INSERT INTO jobs (job_id, title, level_id, company_id) VALUES (?, ?, ?, ?)", [
        (10, 'Job 10', 1, 1),
        (20, 'Job 20', 2, 2),
        (30, 'Job 30', 3, 1)
    ])
    mock_db.commit()

    processed_results = {
        10: ['python', 'react'],
        20: ['python', 'aws'],
        30: ['python']
    }
    
    success = dbQueries.save_processed_skills(processed_results)
    
    assert success is True
    
    skills = cursor.execute("SELECT skill_name FROM skills ORDER BY skill_name").fetchall()
    assert [s[0] for s in skills] == ['aws', 'python', 'react']
    
    job_skills = cursor.execute("SELECT * FROM job_skills").fetchall()
    assert len(job_skills) == 5

    popular = dbQueries.get_popular_skills(top_n=2)
    
    assert len(popular) == 2
    assert popular[0] == ('python', 3)
    
    assert popular[1] == ('aws', 1) or popular[1] == ('react', 1)

def test_find_matching_jobs(mock_db):
    cursor = mock_db.cursor()
    
    cursor.executemany("INSERT INTO skills (skill_name) VALUES (?)", 
        [('Python',), ('React',), ('AWS',), ('SQL',)])

    cursor.executemany("INSERT INTO jobs (job_id, title, level_id, company_id) VALUES (?, ?, ?, ?)", [
        (1, 'Python Dev', 2, 1),
        (2, 'React Dev', 1, 2),
        (3, 'Full Stack', 2, 2)
    ])
    
    cursor.executemany("INSERT INTO job_skills (job_id, skill_id) VALUES (?, ?)", [
        (1, 1), (1, 4), 
        (2, 2), (2, 4),
        (3, 1), (3, 2), (3, 3), (3, 4)
    ])
    mock_db.commit()
    
    user_skills = ['Python', 'SQL']
    target_levels = ['Mid']
    primary_level = 'Mid'
    
    results = dbQueries.find_matching_jobs(user_skills, target_levels, primary_level)

    assert len(results) == 2
    assert results[0]['title'] == 'Python Dev'
    assert results[0]['match_percentage'] == 100
    assert results[1]['title'] == 'Full Stack'
    assert results[1]['match_percentage'] == 50
    
    user_skills_2 = ['React', 'SQL']
    target_levels_2 = ['Junior', 'Mid']
    primary_level_2 = 'Junior'
    
    results_2 = dbQueries.find_matching_jobs(user_skills_2, target_levels_2, primary_level_2)
    
    assert len(results_2) == 3
    assert results_2[0]['title'] == 'React Dev'
    assert results_2[0]['match_percentage'] == 100
    
    remaining_results = [
        (res['title'], res['match_percentage']) for res in results_2[1:]
    ]
    expected_set = {
        ('Python Dev', 25), 
        ('Full Stack', 25)
    }
    assert set(remaining_results) == expected_set