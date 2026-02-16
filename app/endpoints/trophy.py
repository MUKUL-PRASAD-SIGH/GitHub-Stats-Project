"""Achievement trophies endpoint."""
from fastapi import APIRouter, Query, Response
from ..github import graphql, GitHubAPIError, RateLimitError
from ..cache import cache
from ..utils.svg_helpers import create_error_svg, get_theme_colors
from ..utils.trophy import calculate_trophies, get_trophy_color

router = APIRouter()


TROPHY_QUERY = """
query($username: String!) {
  user(login: $username) {
    name
    login
    contributionsCollection {
      totalCommitContributions
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


def generate_trophy_svg(data: dict, theme: str = "dark") -> str:
    """
    Generate SVG for achievement trophies card.
    
    Args:
        data: User data from GitHub API
        theme: Color theme (dark/light)
        
    Returns:
        SVG string
    """
    user = data.get("user", {})
    name = user.get("name") or user.get("login", "Unknown")
    login = user.get("login", "unknown")
    
    # Calculate trophies
    trophies = calculate_trophies(user)
    
    if not trophies:
        return create_error_svg("No trophies earned yet. Keep coding!")
    
    # Get theme colors
    colors = get_theme_colors(theme)
    
    # Calculate card dimensions
    trophies_per_row = 3
    rows = (len(trophies) + trophies_per_row - 1) // trophies_per_row
    trophy_width = 140
    trophy_height = 100
    header_height = 80
    footer_height = 20
    card_height = header_height + (rows * trophy_height) + footer_height
    
    # Start SVG
    svg_parts = [f'''<svg width="495" height="{card_height}" viewBox="0 0 495 {card_height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .header {{ font: 600 18px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['text']}; }}
    .stat-label {{ font: 400 12px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['text_secondary']}; }}
    .trophy-emoji {{ font: 400 36px 'Segoe UI', Ubuntu, sans-serif; }}
    .trophy-name {{ font: 500 12px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['text']}; }}
    .trophy-level {{ font: 700 14px 'Segoe UI', Ubuntu, sans-serif; }}
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(10px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes bounce {{
      0%, 100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(-5px); }}
    }}
    .header-group {{ animation: fadeIn 0.6s ease-out; }}
    .trophy-item {{ animation: fadeIn 0.6s ease-out backwards; }}
    .trophy-item:hover .trophy-emoji {{ animation: bounce 0.5s ease-in-out; }}
  </style>
  
  <!-- Background -->
  <rect width="495" height="{card_height}" fill="{colors['bg']}" rx="4.5"/>
  <rect x="0.5" y="0.5" width="494" height="{card_height - 1}" stroke="{colors['border']}" fill="none" rx="4"/>
  
  <!-- Header -->
  <g class="header-group">
    <text x="25" y="35" class="header">{name}'s Achievements</text>
    <text x="25" y="55" class="stat-label">@{login} • {len(trophies)} trophies earned</text>
  </g>
  
  <!-- Trophies -->''']
    
    # Generate trophy items
    for i, trophy in enumerate(trophies):
        row = i // trophies_per_row
        col = i % trophies_per_row
        
        x = 30 + (col * 155)
        y = header_height + (row * trophy_height)
        
        emoji = trophy["emoji"]
        trophy_name = trophy["name"]
        level = trophy["level"]
        level_color = get_trophy_color(level)
        
        delay = 0.2 + (i * 0.05)
        
        svg_parts.append(f'''
  <g class="trophy-item" style="animation-delay: {delay}s;">
    <!-- Trophy background -->
    <rect x="{x}" y="{y}" width="{trophy_width}" height="{trophy_height - 10}" fill="{colors['border']}" rx="8" opacity="0.3"/>
    
    <!-- Trophy emoji -->
    <text x="{x + trophy_width // 2}" y="{y + 45}" class="trophy-emoji" text-anchor="middle">{emoji}</text>
    
    <!-- Trophy name -->
    <text x="{x + trophy_width // 2}" y="{y + 65}" class="trophy-name" text-anchor="middle">{trophy_name}</text>
    
    <!-- Trophy level -->
    <text x="{x + trophy_width // 2}" y="{y + 82}" class="trophy-level" text-anchor="middle" fill="{level_color}">{level}</text>
  </g>''')
    
    svg_parts.append('\n</svg>')
    
    return ''.join(svg_parts)


@router.get("/trophy")
async def get_trophy(
    user: str = Query(..., description="GitHub username"),
    theme: str = Query("dark", description="Theme (dark/light)")
):
    """
    Generate achievement trophies card.
    
    Args:
        user: GitHub username
        theme: Color theme
        
    Returns:
        SVG image
    """
    # Check cache
    cache_key = f"trophy:{user}:{theme}"
    cached = cache.get(cache_key)
    if cached:
        return Response(content=cached, media_type="image/svg+xml")
    
    try:
        # Fetch data from GitHub
        data = await graphql(TROPHY_QUERY, {"username": user})
        
        if not data.get("user"):
            svg = create_error_svg(f"User '{user}' not found")
            return Response(content=svg, media_type="image/svg+xml")
        
        # Generate SVG
        svg = generate_trophy_svg(data, theme)
        
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
