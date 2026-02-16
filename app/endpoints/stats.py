"""User statistics endpoint."""
from fastapi import APIRouter, Query, Response
from typing import Optional
from ..github import graphql, GitHubAPIError, RateLimitError
from ..cache import cache
from ..utils.svg_helpers import create_error_svg, get_theme_colors
from ..utils.calculations import (
    calculate_total_stars,
    calculate_total_commits,
    format_number
)

router = APIRouter()


STATS_QUERY = """
query($username: String!) {
  user(login: $username) {
    name
    login
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
    }
    repositoriesContributedTo(first: 1, contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) {
      totalCount
    }
    pullRequests(first: 1) {
      totalCount
    }
    issues(first: 1) {
      totalCount
    }
    followers {
      totalCount
    }
    repositories(first: 100, ownerAffiliations: OWNER, orderBy: {direction: DESC, field: STARGAZERS}) {
      totalCount
      nodes {
        stargazers {
          totalCount
        }
      }
    }
  }
}
"""


def generate_stats_svg(data: dict, theme: str = "dark") -> str:
    """
    Generate SVG for user statistics card.
    
    Args:
        data: User data from GitHub API
        theme: Color theme (dark/light)
        
    Returns:
        SVG string
    """
    user = data.get("user", {})
    name = user.get("name") or user.get("login", "Unknown")
    login = user.get("login", "unknown")
    
    # Calculate stats
    total_stars = calculate_total_stars(user.get("repositories", {}).get("nodes", []))
    total_commits = user.get("contributionsCollection", {}).get("totalCommitContributions", 0)
    total_prs = user.get("pullRequests", {}).get("totalCount", 0)
    total_issues = user.get("issues", {}).get("totalCount", 0)
    followers = user.get("followers", {}).get("totalCount", 0)
    total_repos = user.get("repositories", {}).get("totalCount", 0)
    
    # Get theme colors
    colors = get_theme_colors(theme)
    
    # Format numbers
    stars_fmt = format_number(total_stars)
    commits_fmt = format_number(total_commits)
    prs_fmt = format_number(total_prs)
    issues_fmt = format_number(total_issues)
    
    # Generate SVG
    svg = f'''<svg width="495" height="195" viewBox="0 0 495 195" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .header {{ font: 600 18px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['text']}; }}
    .stat-label {{ font: 400 12px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['text_secondary']}; }}
    .stat-value {{ font: 600 16px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['text']}; }}
    .icon {{ fill: {colors['primary']}; }}
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(10px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    .stat-item {{ animation: fadeIn 0.6s ease-out forwards; opacity: 0; }}
    .stat-item:nth-child(1) {{ animation-delay: 0.1s; }}
    .stat-item:nth-child(2) {{ animation-delay: 0.2s; }}
    .stat-item:nth-child(3) {{ animation-delay: 0.3s; }}
    .stat-item:nth-child(4) {{ animation-delay: 0.4s; }}
  </style>
  
  <!-- Background -->
  <rect width="495" height="195" fill="{colors['bg']}" rx="4.5"/>
  <rect x="0.5" y="0.5" width="494" height="194" stroke="{colors['border']}" fill="none" rx="4"/>
  
  <!-- Header -->
  <text x="25" y="35" class="header">{name}'s GitHub Stats</text>
  <text x="25" y="55" class="stat-label">@{login}</text>
  
  <!-- Stats Grid -->
  <g class="stat-item">
    <!-- Total Stars -->
    <svg x="25" y="80" width="16" height="16" viewBox="0 0 16 16" class="icon">
      <path d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z"/>
    </svg>
    <text x="50" y="92" class="stat-value">{stars_fmt}</text>
    <text x="50" y="105" class="stat-label">Total Stars</text>
  </g>
  
  <g class="stat-item">
    <!-- Total Commits -->
    <svg x="145" y="80" width="16" height="16" viewBox="0 0 16 16" class="icon">
      <path d="M11.93 8.5a4.002 4.002 0 01-7.86 0H.75a.75.75 0 010-1.5h3.32a4.002 4.002 0 017.86 0h3.32a.75.75 0 010 1.5h-3.32zM8 6a2 2 0 100 4 2 2 0 000-4z"/>
    </svg>
    <text x="170" y="92" class="stat-value">{commits_fmt}</text>
    <text x="170" y="105" class="stat-label">Total Commits</text>
  </g>
  
  <g class="stat-item">
    <!-- Total PRs -->
    <svg x="290" y="80" width="16" height="16" viewBox="0 0 16 16" class="icon">
      <path d="M7.177 3.073L9.573.677A.25.25 0 0110 .854v4.792a.25.25 0 01-.427.177L7.177 3.427a.25.25 0 010-.354zM3.75 2.5a.75.75 0 100 1.5.75.75 0 000-1.5zm-2.25.75a2.25 2.25 0 113 2.122v5.256a2.251 2.251 0 11-1.5 0V5.372A2.25 2.25 0 011.5 3.25zM11 2.5h-1V4h1a1 1 0 011 1v5.628a2.251 2.251 0 101.5 0V5A2.5 2.5 0 0011 2.5zm1 10.25a.75.75 0 111.5 0 .75.75 0 01-1.5 0zM3.75 12a.75.75 0 100 1.5.75.75 0 000-1.5z"/>
    </svg>
    <text x="315" y="92" class="stat-value">{prs_fmt}</text>
    <text x="315" y="105" class="stat-label">Pull Requests</text>
  </g>
  
  <g class="stat-item">
    <!-- Total Issues -->
    <svg x="25" y="135" width="16" height="16" viewBox="0 0 16 16" class="icon">
      <path d="M8 9.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3z"/>
      <path d="M8 0a8 8 0 100 16A8 8 0 008 0zM1.5 8a6.5 6.5 0 1113 0 6.5 6.5 0 01-13 0z"/>
    </svg>
    <text x="50" y="147" class="stat-value">{issues_fmt}</text>
    <text x="50" y="160" class="stat-label">Issues</text>
  </g>
  
  <g class="stat-item">
    <!-- Followers -->
    <svg x="145" y="135" width="16" height="16" viewBox="0 0 16 16" class="icon">
      <path d="M5.5 3.5a2 2 0 100 4 2 2 0 000-4zM2 5.5a3.5 3.5 0 115.898 2.549 5.507 5.507 0 013.034 4.084.75.75 0 11-1.482.235 4.001 4.001 0 00-7.9 0 .75.75 0 01-1.482-.236A5.507 5.507 0 013.102 8.05 3.49 3.49 0 012 5.5zM11 4a.75.75 0 100 1.5 1.5 1.5 0 01.666 2.844.75.75 0 00-.416.672v.352a.75.75 0 00.574.73c1.2.289 2.162 1.2 2.522 2.372a.75.75 0 101.434-.44 5.01 5.01 0 00-2.56-3.012A3 3 0 0011 4z"/>
    </svg>
    <text x="170" y="147" class="stat-value">{followers}</text>
    <text x="170" y="160" class="stat-label">Followers</text>
  </g>
  
  <g class="stat-item">
    <!-- Total Repos -->
    <svg x="290" y="135" width="16" height="16" viewBox="0 0 16 16" class="icon">
      <path d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 011-1h8zM5 12.25v3.25a.25.25 0 00.4.2l1.45-1.087a.25.25 0 01.3 0L8.6 15.7a.25.25 0 00.4-.2v-3.25a.25.25 0 00-.25-.25h-3.5a.25.25 0 00-.25.25z"/>
    </svg>
    <text x="315" y="147" class="stat-value">{total_repos}</text>
    <text x="315" y="160" class="stat-label">Repositories</text>
  </g>
</svg>'''
    
    return svg


@router.get("/stats")
async def get_stats(
    user: str = Query(..., description="GitHub username"),
    theme: str = Query("dark", description="Theme (dark/light)")
):
    """
    Generate GitHub user statistics card.
    
    Args:
        user: GitHub username
        theme: Color theme
        
    Returns:
        SVG image
    """
    # Check cache
    cache_key = f"stats:{user}:{theme}"
    cached = cache.get(cache_key)
    if cached:
        return Response(content=cached, media_type="image/svg+xml")
    
    try:
        # Fetch data from GitHub
        data = await graphql(STATS_QUERY, {"username": user})
        
        if not data.get("user"):
            svg = create_error_svg(f"User '{user}' not found")
            return Response(content=svg, media_type="image/svg+xml")
        
        # Generate SVG
        svg = generate_stats_svg(data, theme)
        
        # Cache result
        cache.set(cache_key, svg)
        
        # Return with proper headers
        return Response(
            content=svg,
            media_type="image/svg+xml",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Content-Type": "image/svg+xml; charset=utf-8"
            }
        )
        
    except RateLimitError:
        svg = create_error_svg("GitHub API rate limit exceeded")
        return Response(content=svg, media_type="image/svg+xml")
    
    except GitHubAPIError as e:
        svg = create_error_svg(f"GitHub API error: {str(e)}")
        return Response(content=svg, media_type="image/svg+xml")
    
    except Exception as e:
        svg = create_error_svg(f"Error: {str(e)}")
        return Response(content=svg, media_type="image/svg+xml")
