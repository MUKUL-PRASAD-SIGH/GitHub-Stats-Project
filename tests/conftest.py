"""Pytest fixtures and configuration."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.cache import cache


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def mock_github_user_data():
    """Mock GitHub user data for testing."""
    return {
        "user": {
            "name": "Test User",
            "login": "testuser",
            "contributionsCollection": {
                "totalCommitContributions": 1500,
                "restrictedContributionsCount": 0,
                "contributionCalendar": {
                    "totalContributions": 2000,
                    "weeks": [
                        {
                            "contributionDays": [
                                {"date": "2025-01-01", "contributionCount": 5},
                                {"date": "2025-01-02", "contributionCount": 3},
                                {"date": "2025-01-03", "contributionCount": 0},
                                {"date": "2025-01-04", "contributionCount": 8},
                                {"date": "2025-01-05", "contributionCount": 2},
                                {"date": "2025-01-06", "contributionCount": 1},
                                {"date": "2025-01-07", "contributionCount": 0},
                            ]
                        }
                    ]
                }
            },
            "repositoriesContributedTo": {
                "totalCount": 25
            },
            "pullRequests": {
                "totalCount": 150
            },
            "issues": {
                "totalCount": 75
            },
            "followers": {
                "totalCount": 500
            },
            "repositories": {
                "totalCount": 50,
                "nodes": [
                    {"stargazers": {"totalCount": 100}},
                    {"stargazers": {"totalCount": 50}},
                    {"stargazers": {"totalCount": 25}},
                ]
            }
        }
    }
