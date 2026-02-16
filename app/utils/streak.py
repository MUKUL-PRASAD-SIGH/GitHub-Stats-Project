"""Contribution streak calculation utilities."""
from datetime import datetime, timedelta
from typing import Any


def calculate_streak(contribution_calendar: dict[str, Any]) -> dict[str, int]:
    """
    Calculate current and longest contribution streaks.
    
    Args:
        contribution_calendar: Contribution calendar data from GitHub API
        
    Returns:
        Dictionary with current_streak, longest_streak, and total_contributions
    """
    weeks = contribution_calendar.get("weeks", [])
    total_contributions = contribution_calendar.get("totalContributions", 0)
    
    # Flatten all days into a single list
    all_days = []
    for week in weeks:
        for day in week.get("contributionDays", []):
            all_days.append({
                "date": day.get("date"),
                "count": day.get("contributionCount", 0)
            })
    
    if not all_days:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "total_contributions": total_contributions
        }
    
    # Sort by date (should already be sorted, but ensure it)
    all_days.sort(key=lambda x: x["date"])
    
    # Calculate current streak (working backwards from today)
    current_streak = 0
    today = datetime.now().date()
    
    # Start from the most recent day
    for i in range(len(all_days) - 1, -1, -1):
        day_date = datetime.strptime(all_days[i]["date"], "%Y-%m-%d").date()
        day_count = all_days[i]["count"]
        
        # Calculate expected date for streak continuation
        expected_date = today - timedelta(days=current_streak)
        
        if day_date == expected_date:
            if day_count > 0:
                current_streak += 1
            else:
                # If today has no contributions, we can skip it for current streak
                if current_streak == 0:
                    current_streak = 0
                else:
                    break
        elif day_date < expected_date:
            break
    
    # Calculate longest streak
    longest_streak = 0
    temp_streak = 0
    
    for day in all_days:
        if day["count"] > 0:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 0
    
    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_contributions": total_contributions
    }


def get_date_range_text(streak_days: int) -> str:
    """
    Get human-readable date range for a streak.
    
    Args:
        streak_days: Number of days in the streak
        
    Returns:
        Formatted date range string
    """
    if streak_days == 0:
        return "No active streak"
    
    today = datetime.now().date()
    start_date = today - timedelta(days=streak_days - 1)
    
    return f"{start_date.strftime('%b %d, %Y')} - Present"
