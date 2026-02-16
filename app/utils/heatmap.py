"""Contribution heatmap utilities."""
from typing import Any
from datetime import datetime


def get_contribution_color(count: int, theme: str = "dark") -> str:
    """
    Get color for contribution count (GitHub-style).
    
    Args:
        count: Number of contributions
        theme: Color theme
        
    Returns:
        Hex color code
    """
    if theme == "dark":
        if count == 0:
            return "#161b22"
        elif count < 3:
            return "#0e4429"
        elif count < 6:
            return "#006d32"
        elif count < 9:
            return "#26a641"
        else:
            return "#39d353"
    else:  # light theme
        if count == 0:
            return "#ebedf0"
        elif count < 3:
            return "#9be9a8"
        elif count < 6:
            return "#40c463"
        elif count < 9:
            return "#30a14e"
        else:
            return "#216e39"


def process_contribution_calendar(calendar: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Process contribution calendar data for heatmap.
    
    Args:
        calendar: Contribution calendar from GitHub API
        
    Returns:
        List of weeks with contribution data
    """
    weeks = calendar.get("weeks", [])
    processed_weeks = []
    
    for week in weeks:
        days = []
        for day in week.get("contributionDays", []):
            days.append({
                "date": day.get("date"),
                "count": day.get("contributionCount", 0),
                "level": get_contribution_level(day.get("contributionCount", 0))
            })
        processed_weeks.append(days)
    
    return processed_weeks


def get_contribution_level(count: int) -> int:
    """
    Get contribution level (0-4) based on count.
    
    Args:
        count: Number of contributions
        
    Returns:
        Level from 0 to 4
    """
    if count == 0:
        return 0
    elif count < 3:
        return 1
    elif count < 6:
        return 2
    elif count < 9:
        return 3
    else:
        return 4
