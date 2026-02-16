"""Language statistics calculation utilities."""
from typing import Any


def calculate_language_stats(repositories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Calculate language statistics from repositories.
    
    Args:
        repositories: List of repository objects from GitHub API
        
    Returns:
        List of language stats sorted by size (descending)
    """
    language_totals: dict[str, int] = {}
    
    # Aggregate language sizes across all repos
    for repo in repositories:
        languages = repo.get("languages", {}).get("edges", [])
        for lang_edge in languages:
            lang_name = lang_edge.get("node", {}).get("name")
            lang_size = lang_edge.get("size", 0)
            
            if lang_name:
                language_totals[lang_name] = language_totals.get(lang_name, 0) + lang_size
    
    # Calculate total size
    total_size = sum(language_totals.values())
    
    if total_size == 0:
        return []
    
    # Convert to list with percentages
    language_stats = []
    for name, size in language_totals.items():
        percentage = (size / total_size) * 100
        language_stats.append({
            "name": name,
            "size": size,
            "percentage": percentage
        })
    
    # Sort by size (descending)
    language_stats.sort(key=lambda x: x["size"], reverse=True)
    
    return language_stats


def get_language_color(language: str) -> str:
    """
    Get color for a programming language.
    
    Args:
        language: Language name
        
    Returns:
        Hex color code
    """
    # GitHub's official language colors
    colors = {
        "JavaScript": "#f1e05a",
        "TypeScript": "#3178c6",
        "Python": "#3572A5",
        "Java": "#b07219",
        "C": "#555555",
        "C++": "#f34b7d",
        "C#": "#178600",
        "Go": "#00ADD8",
        "Rust": "#dea584",
        "Ruby": "#701516",
        "PHP": "#4F5D95",
        "Swift": "#F05138",
        "Kotlin": "#A97BFF",
        "Dart": "#00B4AB",
        "R": "#198CE7",
        "Shell": "#89e051",
        "HTML": "#e34c26",
        "CSS": "#563d7c",
        "SCSS": "#c6538c",
        "Vue": "#41b883",
        "Jupyter Notebook": "#DA5B0B",
        "Objective-C": "#438eff",
        "Scala": "#c22d40",
        "Perl": "#0298c3",
        "Lua": "#000080",
        "Haskell": "#5e5086",
        "Elixir": "#6e4a7e",
        "Clojure": "#db5855",
        "Vim script": "#199f4b",
        "Dockerfile": "#384d54",
        "Makefile": "#427819",
    }
    
    return colors.get(language, "#858585")  # Default gray
