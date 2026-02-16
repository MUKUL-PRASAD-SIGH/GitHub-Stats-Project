"""Statistical calculations and data processing utilities."""
from typing import Any


def calculate_total_stars(repositories: list[dict[str, Any]]) -> int:
    """
    Calculate total stars across all repositories.
    
    Args:
        repositories: List of repository objects from GitHub API
        
    Returns:
        Total star count
    """
    return sum(repo.get("stargazers", {}).get("totalCount", 0) for repo in repositories)


def calculate_total_commits(contributions: dict[str, Any]) -> int:
    """
    Calculate total commits from contribution data.
    
    Args:
        contributions: Contribution calendar data from GitHub API
        
    Returns:
        Total commit count
    """
    return contributions.get("contributionCalendar", {}).get("totalContributions", 0)


def calculate_total_prs(pull_requests: dict[str, Any]) -> int:
    """
    Calculate total pull requests.
    
    Args:
        pull_requests: Pull request data from GitHub API
        
    Returns:
        Total PR count
    """
    return pull_requests.get("totalCount", 0)


def calculate_total_issues(issues: dict[str, Any]) -> int:
    """
    Calculate total issues.
    
    Args:
        issues: Issue data from GitHub API
        
    Returns:
        Total issue count
    """
    return issues.get("totalCount", 0)


def format_number(num: int) -> str:
    """
    Format large numbers with k/m suffixes.
    
    Args:
        num: Number to format
        
    Returns:
        Formatted string (e.g., "1.2k", "3.4m")
    """
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}m"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}k"
    else:
        return str(num)
