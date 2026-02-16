"""Trophy and achievement calculation utilities."""
from typing import Any


def calculate_trophies(user_data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Calculate achievement trophies based on user statistics.
    
    Args:
        user_data: User data from GitHub API
        
    Returns:
        List of earned trophies
    """
    trophies = []
    
    # Extract stats
    followers = user_data.get("followers", {}).get("totalCount", 0)
    repos = user_data.get("repositories", {}).get("totalCount", 0)
    stars = sum(
        repo.get("stargazers", {}).get("totalCount", 0)
        for repo in user_data.get("repositories", {}).get("nodes", [])
    )
    commits = user_data.get("contributionsCollection", {}).get("totalCommitContributions", 0)
    prs = user_data.get("pullRequests", {}).get("totalCount", 0)
    issues = user_data.get("issues", {}).get("totalCount", 0)
    
    # Commit Trophies
    if commits >= 10000:
        trophies.append({"emoji": "🔥", "name": "Commit Legend", "level": "SSS"})
    elif commits >= 5000:
        trophies.append({"emoji": "🔥", "name": "Commit Master", "level": "SS"})
    elif commits >= 2000:
        trophies.append({"emoji": "💪", "name": "Commit Hero", "level": "S"})
    elif commits >= 1000:
        trophies.append({"emoji": "⚡", "name": "Commit Pro", "level": "A"})
    elif commits >= 500:
        trophies.append({"emoji": "✨", "name": "Active Coder", "level": "B"})
    
    # Star Trophies
    if stars >= 10000:
        trophies.append({"emoji": "🌟", "name": "Star Legend", "level": "SSS"})
    elif stars >= 5000:
        trophies.append({"emoji": "🌟", "name": "Star Master", "level": "SS"})
    elif stars >= 1000:
        trophies.append({"emoji": "⭐", "name": "Star Collector", "level": "S"})
    elif stars >= 500:
        trophies.append({"emoji": "⭐", "name": "Rising Star", "level": "A"})
    elif stars >= 100:
        trophies.append({"emoji": "✨", "name": "Stargazer", "level": "B"})
    
    # Repository Trophies
    if repos >= 100:
        trophies.append({"emoji": "📦", "name": "Repo Master", "level": "SS"})
    elif repos >= 50:
        trophies.append({"emoji": "📦", "name": "Prolific Builder", "level": "S"})
    elif repos >= 20:
        trophies.append({"emoji": "🏗️", "name": "Builder", "level": "A"})
    elif repos >= 10:
        trophies.append({"emoji": "🔨", "name": "Creator", "level": "B"})
    
    # Follower Trophies
    if followers >= 10000:
        trophies.append({"emoji": "👑", "name": "Influencer King", "level": "SSS"})
    elif followers >= 5000:
        trophies.append({"emoji": "🎯", "name": "Top Influencer", "level": "SS"})
    elif followers >= 1000:
        trophies.append({"emoji": "🌐", "name": "Influencer", "level": "S"})
    elif followers >= 500:
        trophies.append({"emoji": "📢", "name": "Well Known", "level": "A"})
    elif followers >= 100:
        trophies.append({"emoji": "👥", "name": "Popular", "level": "B"})
    
    # Pull Request Trophies
    if prs >= 1000:
        trophies.append({"emoji": "🔀", "name": "PR Legend", "level": "SS"})
    elif prs >= 500:
        trophies.append({"emoji": "🔀", "name": "PR Master", "level": "S"})
    elif prs >= 100:
        trophies.append({"emoji": "🤝", "name": "Collaborator", "level": "A"})
    elif prs >= 50:
        trophies.append({"emoji": "🤝", "name": "Team Player", "level": "B"})
    
    # Issue Trophies
    if issues >= 500:
        trophies.append({"emoji": "🐛", "name": "Bug Hunter", "level": "S"})
    elif issues >= 100:
        trophies.append({"emoji": "🔍", "name": "Issue Tracker", "level": "A"})
    
    # Special Achievements
    if commits > 0 and stars > 0 and followers > 0:
        trophies.append({"emoji": "🎖️", "name": "All-Rounder", "level": "S"})
    
    if len(trophies) >= 10:
        trophies.append({"emoji": "🏆", "name": "Achievement Hunter", "level": "SS"})
    
    return trophies


def get_trophy_color(level: str) -> str:
    """
    Get color for trophy level.
    
    Args:
        level: Trophy level (SSS, SS, S, A, B)
        
    Returns:
        Hex color code
    """
    colors = {
        "SSS": "#FFD700",  # Gold
        "SS": "#C0C0C0",   # Silver
        "S": "#CD7F32",    # Bronze
        "A": "#4169E1",    # Royal Blue
        "B": "#32CD32",    # Lime Green
    }
    return colors.get(level, "#858585")
