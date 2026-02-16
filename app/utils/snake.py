"""Snake animation generation for contribution graph."""
from typing import Any
import random


def generate_snake_path(weeks: list[list[dict[str, Any]]]) -> list[tuple[int, int]]:
    """
    Generate snake path through contribution graph.
    
    Args:
        weeks: Processed contribution calendar weeks
        
    Returns:
        List of (x, y) coordinates for snake path
    """
    if not weeks:
        return []
    
    path = []
    
    # Start from top-left
    x, y = 0, 0
    path.append((x, y))
    
    # Snake through the grid in a zig-zag pattern
    for week_idx in range(len(weeks)):
        week = weeks[week_idx]
        
        if week_idx % 2 == 0:
            # Go down
            for day_idx in range(len(week)):
                if not (week_idx == 0 and day_idx == 0):  # Skip first cell
                    path.append((week_idx, day_idx))
        else:
            # Go up
            for day_idx in range(len(week) - 1, -1, -1):
                path.append((week_idx, day_idx))
    
    return path


def calculate_snake_length(calendar: dict[str, Any], max_length: int = 500) -> int:
    """
    Calculate snake length based on contributions.
    
    Args:
        calendar: Contribution calendar data
        max_length: Maximum snake length
        
    Returns:
        Snake length
    """
    total = calendar.get("totalContributions", 0)
    
    # Scale snake length based on contributions
    if total == 0:
        return 10
    elif total < 100:
        return min(50, total)
    elif total < 500:
        return min(150, total // 2)
    else:
        return min(max_length, total // 5)
