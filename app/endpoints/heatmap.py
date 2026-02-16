"""Contribution heatmap endpoint."""
from fastapi import APIRouter, Query, Response
from ..github import graphql, GitHubAPIError, RateLimitError
from ..cache import cache
from ..utils.svg_helpers import create_error_svg, get_theme_colors
from ..utils.heatmap import process_contribution_calendar, get_contribution_color

router = APIRouter()


HEATMAP_QUERY = """
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


def generate_heatmap_svg(data: dict, theme: str = "dark") -> str:
    """
    Generate SVG for contribution heatmap.
    
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
    total_contributions = calendar.get("totalContributions", 0)
    weeks = process_contribution_calendar(calendar)
    
    if not weeks:
        return create_error_svg("No contribution data available")
    
    # Get theme colors
    colors = get_theme_colors(theme)
    
    # Heatmap dimensions
    cell_size = 10
    cell_gap = 3
    weeks_to_show = min(len(weeks), 53)  # Show last 53 weeks (1 year)
    start_week = max(0, len(weeks) - weeks_to_show)
    
    heatmap_width = weeks_to_show * (cell_size + cell_gap)
    heatmap_height = 7 * (cell_size + cell_gap)
    
    header_height = 80
    legend_height = 40
    card_width = heatmap_width + 50
    card_height = header_height + heatmap_height + legend_height
    
    # Start SVG
    svg_parts = [f'''<svg width="{card_width}" height="{card_height}" viewBox="0 0 {card_width} {card_height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .header {{ font: 600 18px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['text']}; }}
    .stat-label {{ font: 400 12px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['text_secondary']}; }}
    .legend-text {{ font: 400 10px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['text_secondary']}; }}
    @keyframes fadeIn {{
      from {{ opacity: 0; }}
      to {{ opacity: 1; }}
    }}
    .header-group {{ animation: fadeIn 0.6s ease-out; }}
    .heatmap-cell {{ animation: fadeIn 0.8s ease-out backwards; }}
  </style>
  
  <!-- Background -->
  <rect width="{card_width}" height="{card_height}" fill="{colors['bg']}" rx="4.5"/>
  <rect x="0.5" y="0.5" width="{card_width - 1}" height="{card_height - 1}" stroke="{colors['border']}" fill="none" rx="4"/>
  
  <!-- Header -->
  <g class="header-group">
    <text x="25" y="35" class="header">{name}'s Contribution Heatmap</text>
    <text x="25" y="55" class="stat-label">@{login} • {total_contributions} contributions in the last year</text>
  </g>
  
  <!-- Heatmap -->
  <g transform="translate(25, {header_height})">''']
    
    # Generate heatmap cells
    for week_idx in range(start_week, len(weeks)):
        week = weeks[week_idx]
        x_offset = (week_idx - start_week) * (cell_size + cell_gap)
        
        for day_idx, day in enumerate(week):
            y_offset = day_idx * (cell_size + cell_gap)
            count = day["count"]
            color = get_contribution_color(count, theme)
            
            # Animation delay based on position
            delay = (week_idx - start_week) * 0.01
            
            svg_parts.append(f'''
    <rect class="heatmap-cell" x="{x_offset}" y="{y_offset}" width="{cell_size}" height="{cell_size}" fill="{color}" rx="2" style="animation-delay: {delay}s;">
      <title>{day['date']}: {count} contributions</title>
    </rect>''')
    
    svg_parts.append('''
  </g>
  
  <!-- Legend -->''')
    
    legend_y = header_height + heatmap_height + 20
    legend_x = card_width - 150
    
    svg_parts.append(f'''
  <g transform="translate({legend_x}, {legend_y})">
    <text x="0" y="10" class="legend-text">Less</text>''')
    
    for i in range(5):
        color = get_contribution_color(i * 3, theme)
        x_pos = 30 + (i * 15)
        svg_parts.append(f'''
    <rect x="{x_pos}" y="0" width="{cell_size}" height="{cell_size}" fill="{color}" rx="2"/>''')
    
    svg_parts.append(f'''
    <text x="{30 + 5 * 15 + 10}" y="10" class="legend-text">More</text>
  </g>
</svg>''')
    
    return ''.join(svg_parts)


@router.get("/heatmap")
async def get_heatmap(
    user: str = Query(..., description="GitHub username"),
    theme: str = Query("dark", description="Theme (dark/light)")
):
    """
    Generate contribution heatmap.
    
    Args:
        user: GitHub username
        theme: Color theme
        
    Returns:
        SVG image
    """
    # Check cache
    cache_key = f"heatmap:{user}:{theme}"
    cached = cache.get(cache_key)
    if cached:
        return Response(content=cached, media_type="image/svg+xml")
    
    try:
        # Fetch data from GitHub
        data = await graphql(HEATMAP_QUERY, {"username": user})
        
        if not data.get("user"):
            svg = create_error_svg(f"User '{user}' not found")
            return Response(content=svg, media_type="image/svg+xml")
        
        # Generate SVG
        svg = generate_heatmap_svg(data, theme)
        
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
