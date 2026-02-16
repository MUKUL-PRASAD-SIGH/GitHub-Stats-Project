"""Contribution streak endpoint."""
from fastapi import APIRouter, Query, Response
from ..github import graphql, GitHubAPIError, RateLimitError
from ..cache import cache
from ..utils.svg_helpers import create_error_svg, get_theme_colors
from ..utils.streak import calculate_streak, get_date_range_text
from ..utils.calculations import format_number

router = APIRouter()


STREAK_QUERY = """
query($username: String!) {
  user(login: $username) {
    name
    login
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""


def generate_streak_svg(data: dict, theme: str = "dark") -> str:
    """
    Generate SVG for contribution streak card.
    
    Args:
        data: User data from GitHub API
        theme: Color theme (dark/light)
        
    Returns:
        SVG string
    """
    user = data.get("user", {})
    name = user.get("name") or user.get("login", "Unknown")
    login = user.get("login", "unknown")
    
    # Get contribution calendar
    calendar = user.get("contributionsCollection", {}).get("contributionCalendar", {})
    
    # Calculate streaks
    streak_data = calculate_streak(calendar)
    current_streak = streak_data["current_streak"]
    longest_streak = streak_data["longest_streak"]
    total_contributions = streak_data["total_contributions"]
    
    # Get theme colors
    colors = get_theme_colors(theme)
    
    # Format numbers
    total_fmt = format_number(total_contributions)
    
    # Get date range
    date_range = get_date_range_text(current_streak)
    
    # Determine fire emoji intensity based on streak
    fire_emoji = "🔥" if current_streak > 0 else "💤"
    if current_streak > 30:
        fire_emoji = "🔥🔥🔥"
    elif current_streak > 7:
        fire_emoji = "🔥🔥"
    
    # Generate SVG
    svg = f'''<svg width="495" height="195" viewBox="0 0 495 195" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .header {{ font: 600 18px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['text']}; }}
    .stat-label {{ font: 400 12px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['text_secondary']}; }}
    .stat-value {{ font: 700 32px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['primary']}; }}
    .stat-value-small {{ font: 600 20px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['text']}; }}
    .date-text {{ font: 400 11px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['text_secondary']}; }}
    .emoji {{ font: 400 40px 'Segoe UI', Ubuntu, sans-serif; }}
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(10px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes scaleIn {{
      from {{ opacity: 0; transform: scale(0.8); }}
      to {{ opacity: 1; transform: scale(1); }}
    }}
    @keyframes flame {{
      0%, 100% {{ transform: translateY(0) scale(1); }}
      50% {{ transform: translateY(-3px) scale(1.05); }}
    }}
    .header-group {{ animation: fadeIn 0.6s ease-out; }}
    .streak-main {{ animation: scaleIn 0.8s ease-out 0.2s backwards; }}
    .streak-stats {{ animation: fadeIn 0.6s ease-out 0.4s backwards; }}
    .fire {{ animation: flame 2s ease-in-out infinite; transform-origin: center; }}
  </style>
  
  <!-- Background -->
  <rect width="495" height="195" fill="{colors['bg']}" rx="4.5"/>
  <rect x="0.5" y="0.5" width="494" height="194" stroke="{colors['border']}" fill="none" rx="4"/>
  
  <!-- Header -->
  <g class="header-group">
    <text x="25" y="35" class="header">{name}'s Contribution Streak</text>
    <text x="25" y="55" class="stat-label">@{login}</text>
  </g>
  
  <!-- Main Streak Display -->
  <g class="streak-main">
    <text x="247.5" y="75" class="emoji fire" text-anchor="middle">{fire_emoji}</text>
    <text x="247.5" y="125" class="stat-value" text-anchor="middle">{current_streak}</text>
    <text x="247.5" y="145" class="stat-label" text-anchor="middle">Current Streak (days)</text>
    <text x="247.5" y="162" class="date-text" text-anchor="middle">{date_range}</text>
  </g>
  
  <!-- Stats Row -->
  <g class="streak-stats">
    <!-- Longest Streak -->
    <rect x="25" y="170" width="140" height="1" fill="{colors['border']}"/>
    <text x="95" y="185" class="stat-value-small" text-anchor="middle">{longest_streak}</text>
    <text x="25" y="185" class="stat-label">Longest:</text>
    
    <!-- Total Contributions -->
    <rect x="330" y="170" width="140" height="1" fill="{colors['border']}"/>
    <text x="400" y="185" class="stat-value-small" text-anchor="middle">{total_fmt}</text>
    <text x="330" y="185" class="stat-label">Total:</text>
  </g>
</svg>'''
    
    return svg


@router.get("/streak")
async def get_streak(
    user: str = Query(..., description="GitHub username"),
    theme: str = Query("dark", description="Theme (dark/light)")
):
    """
    Generate GitHub contribution streak card.
    
    Args:
        user: GitHub username
        theme: Color theme
        
    Returns:
        SVG image
    """
    # Check cache
    cache_key = f"streak:{user}:{theme}"
    cached = cache.get(cache_key)
    if cached:
        return Response(content=cached, media_type="image/svg+xml")
    
    try:
        # Fetch data from GitHub
        data = await graphql(STREAK_QUERY, {"username": user})
        
        if not data.get("user"):
            svg = create_error_svg(f"User '{user}' not found")
            return Response(content=svg, media_type="image/svg+xml")
        
        # Generate SVG
        svg = generate_streak_svg(data, theme)
        
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
