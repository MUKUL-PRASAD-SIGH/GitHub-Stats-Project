"""Tests for utility functions."""
import pytest
from app.utils.calculations import calculate_total_stars, format_number
from app.utils.streak import calculate_streak, get_date_range_text
from app.utils.languages import get_language_color
from app.utils.trophy import calculate_trophies, get_trophy_color
from app.utils.heatmap import get_contribution_color, get_contribution_level


class TestCalculations:
    """Test calculation utilities."""
    
    def test_calculate_total_stars(self):
        """Test total stars calculation."""
        repos = [
            {"stargazers": {"totalCount": 100}},
            {"stargazers": {"totalCount": 50}},
            {"stargazers": {"totalCount": 25}},
        ]
        assert calculate_total_stars(repos) == 175
    
    def test_calculate_total_stars_empty(self):
        """Test total stars with empty list."""
        assert calculate_total_stars([]) == 0
    
    def test_format_number_thousands(self):
        """Test number formatting for thousands."""
        assert format_number(1500) == "1.5k"
        assert format_number(999) == "999"
    
    def test_format_number_millions(self):
        """Test number formatting for millions."""
        assert format_number(1500000) == "1.5m"
        assert format_number(1000000) == "1.0m"


class TestStreak:
    """Test streak utilities."""
    
    def test_calculate_streak_active(self):
        """Test streak calculation with active streak."""
        calendar = {
            "totalContributions": 10,
            "weeks": [
                {
                    "contributionDays": [
                        {"date": "2025-01-01", "contributionCount": 5},
                        {"date": "2025-01-02", "contributionCount": 3},
                        {"date": "2025-01-03", "contributionCount": 2},
                    ]
                }
            ]
        }
        result = calculate_streak(calendar)
        assert "current_streak" in result
        assert "longest_streak" in result
        assert "total_contributions" in result
        assert result["total_contributions"] == 10
    
    def test_calculate_streak_empty(self):
        """Test streak calculation with empty calendar."""
        calendar = {"totalContributions": 0, "weeks": []}
        result = calculate_streak(calendar)
        assert result["current_streak"] == 0
        assert result["longest_streak"] == 0
        assert result["total_contributions"] == 0


class TestLanguages:
    """Test language utilities."""
    
    def test_calculate_language_stats(self):
        """Test language stats calculation."""
        repositories = [
            {
                "languages": {
                    "edges": [
                        {"size": 10000, "node": {"name": "Python"}},
                        {"size": 5000, "node": {"name": "JavaScript"}},
                    ]
                }
            }
        ]
        from app.utils.languages import calculate_language_stats
        stats = calculate_language_stats(repositories)
        
        assert len(stats) == 2
        assert stats[0]["name"] == "Python"
        assert stats[0]["size"] == 10000
        assert stats[0]["percentage"] == pytest.approx(66.67, rel=0.01)
    
    def test_get_language_color(self):
        """Test language color mapping."""
        assert get_language_color("Python") == "#3572A5"
        assert get_language_color("JavaScript") == "#f1e05a"
        assert get_language_color("UnknownLang") == "#858585"  # Default


class TestTrophy:
    """Test trophy utilities."""
    
    def test_calculate_trophies_high_stats(self):
        """Test trophy calculation with high stats."""
        user_data = {
            "contributionsCollection": {"totalCommitContributions": 5000},
            "repositories": {
                "totalCount": 100,
                "nodes": [{"stargazers": {"totalCount": 10000}}]
            },
            "followers": {"totalCount": 10000},
            "pullRequests": {"totalCount": 1000},
            "issues": {"totalCount": 500},
        }
        trophies = calculate_trophies(user_data)
        
        assert len(trophies) > 0
        # Should have SSS level trophies
        sss_trophies = [t for t in trophies if t["level"] == "SSS"]
        assert len(sss_trophies) > 0
    
    def test_calculate_trophies_low_stats(self):
        """Test trophy calculation with low stats."""
        user_data = {
            "contributionsCollection": {"totalCommitContributions": 0},
            "repositories": {"totalCount": 0, "nodes": []},
            "followers": {"totalCount": 0},
            "pullRequests": {"totalCount": 0},
            "issues": {"totalCount": 0},
        }
        trophies = calculate_trophies(user_data)
        
        assert len(trophies) == 0
    
    def test_get_trophy_color(self):
        """Test trophy color mapping."""
        assert get_trophy_color("SSS") == "#FFD700"  # Gold
        assert get_trophy_color("SS") == "#C0C0C0"   # Silver
        assert get_trophy_color("S") == "#CD7F32"    # Bronze


class TestHeatmap:
    """Test heatmap utilities."""
    
    def test_get_contribution_color_dark(self):
        """Test contribution color for dark theme."""
        assert get_contribution_color(0, "dark") == "#161b22"
        assert get_contribution_color(1, "dark") == "#0e4429"
        assert get_contribution_color(10, "dark") == "#39d353"
    
    def test_get_contribution_color_light(self):
        """Test contribution color for light theme."""
        assert get_contribution_color(0, "light") == "#ebedf0"
        assert get_contribution_color(1, "light") == "#9be9a8"
        assert get_contribution_color(10, "light") == "#216e39"
    
    def test_get_contribution_level(self):
        """Test contribution level calculation."""
        assert get_contribution_level(0) == 0
        assert get_contribution_level(1) == 1
        assert get_contribution_level(5) == 2
        assert get_contribution_level(8) == 3
        assert get_contribution_level(10) == 4
