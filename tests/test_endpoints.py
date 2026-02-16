"""Tests for API endpoints."""
import pytest
from unittest.mock import patch, AsyncMock


class TestHealthEndpoints:
    """Test health and info endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "GitHub Profile API"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
        assert "/stats" in data["endpoints"]
        assert "/streak" in data["endpoints"]
        assert "/languages" in data["endpoints"]
        assert "/trophy" in data["endpoints"]
        assert "/heatmap" in data["endpoints"]
        assert "/snake" in data["endpoints"]
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestStatsEndpoint:
    """Test /stats endpoint."""
    
    @patch('app.endpoints.stats.graphql')
    async def test_stats_success(self, mock_graphql, client, mock_github_user_data):
        """Test successful stats generation."""
        mock_graphql.return_value = mock_github_user_data
        
        response = client.get("/stats?user=testuser")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/svg+xml; charset=utf-8"
        assert b"<svg" in response.content
        assert b"Test User" in response.content
    
    def test_stats_missing_user(self, client):
        """Test stats endpoint without user parameter."""
        response = client.get("/stats")
        assert response.status_code == 422  # Validation error
    
    @patch('app.endpoints.stats.graphql')
    async def test_stats_user_not_found(self, mock_graphql, client):
        """Test stats with non-existent user."""
        mock_graphql.return_value = {"user": None}
        
        response = client.get("/stats?user=nonexistent")
        assert response.status_code == 200
        assert b"not found" in response.content.lower()
    
    @patch('app.endpoints.stats.graphql')
    async def test_stats_theme_light(self, mock_graphql, client, mock_github_user_data):
        """Test stats with light theme."""
        mock_graphql.return_value = mock_github_user_data
        
        response = client.get("/stats?user=testuser&theme=light")
        assert response.status_code == 200
        assert b"#ffffff" in response.content  # Light background
    
    @patch('app.endpoints.stats.graphql')
    async def test_stats_theme_dark(self, mock_graphql, client, mock_github_user_data):
        """Test stats with dark theme."""
        mock_graphql.return_value = mock_github_user_data
        
        response = client.get("/stats?user=testuser&theme=dark")
        assert response.status_code == 200
        assert b"#1a1b27" in response.content  # Dark background


class TestStreakEndpoint:
    """Test /streak endpoint."""
    
    @patch('app.endpoints.streak.graphql')
    async def test_streak_success(self, mock_graphql, client, mock_github_user_data):
        """Test successful streak generation."""
        mock_graphql.return_value = mock_github_user_data
        
        response = client.get("/streak?user=testuser")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/svg+xml; charset=utf-8"
        assert b"<svg" in response.content
        assert b"Contribution Streak" in response.content
    
    def test_streak_missing_user(self, client):
        """Test streak endpoint without user parameter."""
        response = client.get("/streak")
        assert response.status_code == 422


class TestLanguagesEndpoint:
    """Test /languages endpoint."""
    
    @patch('app.endpoints.languages.graphql')
    async def test_languages_success(self, mock_graphql, client):
        """Test successful languages generation."""
        mock_data = {
            "user": {
                "name": "Test User",
                "login": "testuser",
                "repositories": {
                    "nodes": [
                        {
                            "languages": {
                                "edges": [
                                    {"size": 10000, "node": {"name": "Python"}},
                                    {"size": 5000, "node": {"name": "JavaScript"}},
                                ]
                            }
                        }
                    ]
                }
            }
        }
        mock_graphql.return_value = mock_data
        
        response = client.get("/languages?user=testuser")
        assert response.status_code == 200
        assert b"<svg" in response.content
        assert b"Top Languages" in response.content
    
    @patch('app.endpoints.languages.graphql')
    async def test_languages_with_limit(self, mock_graphql, client):
        """Test languages with custom limit."""
        mock_data = {
            "user": {
                "name": "Test User",
                "login": "testuser",
                "repositories": {
                    "nodes": [
                        {
                            "languages": {
                                "edges": [
                                    {"size": 10000, "node": {"name": "Python"}},
                                ]
                            }
                        }
                    ]
                }
            }
        }
        mock_graphql.return_value = mock_data
        
        response = client.get("/languages?user=testuser&limit=3")
        assert response.status_code == 200


class TestTrophyEndpoint:
    """Test /trophy endpoint."""
    
    @patch('app.endpoints.trophy.graphql')
    async def test_trophy_success(self, mock_graphql, client, mock_github_user_data):
        """Test successful trophy generation."""
        mock_graphql.return_value = mock_github_user_data
        
        response = client.get("/trophy?user=testuser")
        assert response.status_code == 200
        assert b"<svg" in response.content
        assert b"Achievements" in response.content
    
    @patch('app.endpoints.trophy.graphql')
    async def test_trophy_no_trophies(self, mock_graphql, client):
        """Test trophy with user having no achievements."""
        mock_data = {
            "user": {
                "name": "New User",
                "login": "newuser",
                "contributionsCollection": {"totalCommitContributions": 0},
                "pullRequests": {"totalCount": 0},
                "issues": {"totalCount": 0},
                "followers": {"totalCount": 0},
                "repositories": {"totalCount": 0, "nodes": []}
            }
        }
        mock_graphql.return_value = mock_data
        
        response = client.get("/trophy?user=newuser")
        assert response.status_code == 200
        assert b"No trophies" in response.content


class TestHeatmapEndpoint:
    """Test /heatmap endpoint."""
    
    @patch('app.endpoints.heatmap.graphql')
    async def test_heatmap_success(self, mock_graphql, client, mock_github_user_data):
        """Test successful heatmap generation."""
        mock_graphql.return_value = mock_github_user_data
        
        response = client.get("/heatmap?user=testuser")
        assert response.status_code == 200
        assert b"<svg" in response.content
        assert b"Contribution Heatmap" in response.content
    
    def test_heatmap_missing_user(self, client):
        """Test heatmap endpoint without user parameter."""
        response = client.get("/heatmap")
        assert response.status_code == 422


class TestSnakeEndpoint:
    """Test /snake endpoint."""
    
    @patch('app.endpoints.snake.graphql')
    async def test_snake_success(self, mock_graphql, client, mock_github_user_data):
        """Test successful snake generation."""
        mock_graphql.return_value = mock_github_user_data
        
        response = client.get("/snake?user=testuser")
        assert response.status_code == 200
        assert b"<svg" in response.content
        assert b"Contribution Snake" in response.content
        assert b"polyline" in response.content  # Snake path
    
    def test_snake_missing_user(self, client):
        """Test snake endpoint without user parameter."""
        response = client.get("/snake")
        assert response.status_code == 422


class TestCaching:
    """Test caching functionality."""
    
    @patch('app.endpoints.stats.graphql')
    async def test_cache_hit(self, mock_graphql, client, mock_github_user_data):
        """Test that second request uses cache."""
        mock_graphql.return_value = mock_github_user_data
        
        # First request
        response1 = client.get("/stats?user=testuser")
        assert response1.status_code == 200
        
        # Second request should use cache
        response2 = client.get("/stats?user=testuser")
        assert response2.status_code == 200
        
        # GraphQL should only be called once
        assert mock_graphql.call_count == 1
        
        # Responses should be identical
        assert response1.content == response2.content


class TestErrorHandling:
    """Test error handling."""
    
    @patch('app.endpoints.stats.graphql')
    async def test_rate_limit_error(self, mock_graphql, client):
        """Test rate limit error handling."""
        from app.github import RateLimitError
        mock_graphql.side_effect = RateLimitError("Rate limit exceeded")
        
        response = client.get("/stats?user=testuser")
        assert response.status_code == 200
        assert b"rate limit" in response.content.lower()
    
    @patch('app.endpoints.stats.graphql')
    async def test_api_error(self, mock_graphql, client):
        """Test API error handling."""
        from app.github import GitHubAPIError
        mock_graphql.side_effect = GitHubAPIError("API error")
        
        response = client.get("/stats?user=testuser")
        assert response.status_code == 200
        assert b"error" in response.content.lower()
