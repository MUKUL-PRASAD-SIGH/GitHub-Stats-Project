"""Snake animation endpoint."""
from fastapi import APIRouter, Query, Response
from ..github import graphql, GitHubAPIError, RateLimitError
from ..cache import cache
from ..utils.svg_helpers import create_error_svg, get_theme_colors
from ..utils.heatmap import process_contribution_calendar, get_contribution_color
from ..utils.snake import generate_snake_path, calculate_snake_length

router = APIRouter()


SNAKE_QUERY = """
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


def generate_snake_svg(data: dict, theme: str = "dark") -> str:
    """
    Generate SVG for snake animation eating contributions.
    
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
    weeks = process_contribution_calendar(calendar)
    
    if not weeks:
        return create_error_svg("No contribution data available")
    
    # Get theme colors
    colors = get_theme_colors(theme)
    
    # Grid dimensions
    cell_size = 10
    cell_gap = 3
    weeks_to_show = min(len(weeks), 53)
    start_week = max(0, len(weeks) - weeks_to_show)
    
    grid_width = weeks_to_show * (cell_size + cell_gap)
    grid_height = 7 * (cell_size + cell_gap)
    
    header_height = 80
    footer_height = 20
    card_width = grid_width + 50
    card_height = header_height + grid_height + footer_height
    
    # Generate snake path
    path_coords = generate_snake_path(weeks[start_week:])
    snake_length = calculate_snake_length(calendar)
    
    # Snake color
    snake_color = colors['primary']
    
    # Create path string for animation
    path_points = []
    for x, y in path_coords[:snake_length]:
        px = 25 + x * (cell_size + cell_gap) + cell_size / 2
        py = header_height + y * (cell_size + cell_gap) + cell_size / 2
        path_points.append(f"{px},{py}")
    
    path_data = " ".join(path_points)
    
    # Start SVG
    svg = f'''<svg width="{card_width}" height="{card_height}" viewBox="0 0 {card_width} {card_height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .header {{ font: 600 18px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['text']}; }}
    .stat-label {{ font: 400 12px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['text_secondary']}; }}
    @keyframes fadeIn {{
      from {{ opacity: 0; }}
      to {{ opacity: 1; }}
    }}
    @keyframes snakeMove {{
      0% {{ stroke-dashoffset: {len(path_points) * 15}; }}
      100% {{ stroke-dashoffset: 0; }}
    }}
    .header-group {{ animation: fadeIn 0.6s ease-out; }}
    .grid-cell {{ animation: fadeIn 0.8s ease-out backwards; }}
    .snake-path {{
      stroke-dasharray: {len(path_points) * 15};
      stroke-dashoffset: {len(path_points) * 15};
      animation: snakeMove 10s ease-in-out infinite;
    }}
  </style>
  
  <!-- Background -->
  <rect width="{card_width}" height="{card_height}" fill="{colors['bg']}" rx="4.5"/>
  <rect x="0.5" y="0.5" width="{card_width - 1}" height="{card_height - 1}" stroke="{colors['border']}" fill="none" rx="4"/>
  
  <!-- Header -->
  <g class="header-group">
    <text x="25" y="35" class="header">{name}'s Contribution Snake</text>
    <text x="25" y="55" class="stat-label">@{login} • Snake eating {snake_length} contributions</text>
  </g>
  
  <!-- Contribution Grid -->
  <g>'''
    
    # Draw contribution grid (faded)
    for week_idx in range(start_week, len(weeks)):
        week = weeks[week_idx]
        x_offset = 25 + (week_idx - start_week) * (cell_size + cell_gap)
        
        for day_idx, day in enumerate(week):
            y_offset = header_height + day_idx * (cell_size + cell_gap)
            count = day["count"]
            color = get_contribution_color(count, theme)
            
            svg += f'''
    <rect class="grid-cell" x="{x_offset}" y="{y_offset}" width="{cell_size}" height="{cell_size}" fill="{color}" opacity="0.3" rx="2"/>'''
    
    svg += '''
  </g>
  
  <!-- Snake Path -->'''
    
    if len(path_points) > 1:
        svg += f'''
  <polyline class="snake-path" points="{path_data}" fill="none" stroke="{snake_color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  
  <!-- Snake Head -->
  <circle r="6" fill="{snake_color}">
    <animateMotion dur="10s" repeatCount="indefinite">
      <mpath href="#snakePath"/>
    </animateMotion>
  </circle>
  
  <path id="snakePath" d="M {path_data.replace(',', ' L ')}" fill="none" stroke="none"/>'''
    
    svg += '''
</svg>'''
    
    return svg


@router.get("/snake")
async def get_snake(
    user: str = Query(..., description="GitHub username"),
    theme: str = Query("dark", description="Theme (dark/light)")
):
    """
    Generate snake animation eating contributions.
    
    Args:
        user: GitHub username
        theme: Color theme
        
    Returns:
        SVG image
    """
    # Check cache
    cache_key = f"snake:{user}:{theme}"
    cached = cache.get(cache_key)
    if cached:
        return Response(content=cached, media_type="image/svg+xml")
    
    try:
        # Fetch data from GitHub
        data = await graphql(SNAKE_QUERY, {"username": user})
        
        if not data.get("user"):
            svg = create_error_svg(f"User '{user}' not found")
            return Response(content=svg, media_type="image/svg+xml")
        
        # Generate SVG
        svg = generate_snake_svg(data, theme)
        
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
