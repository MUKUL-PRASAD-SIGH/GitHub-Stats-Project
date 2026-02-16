"""Top languages endpoint."""
from fastapi import APIRouter, Query, Response
from ..github import graphql, GitHubAPIError, RateLimitError
from ..cache import cache
from ..utils.svg_helpers import create_error_svg, get_theme_colors
from ..utils.languages import calculate_language_stats, get_language_color

router = APIRouter()


LANGUAGES_QUERY = """
query($username: String!) {
  user(login: $username) {
    name
    login
    repositories(first: 100, ownerAffiliations: OWNER, orderBy: {direction: DESC, field: STARGAZERS}) {
      nodes {
        name
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node {
              name
              color
            }
          }
        }
      }
    }
  }
}
"""


def generate_languages_svg(data: dict, theme: str = "dark", limit: int = 5) -> str:
    """
    Generate SVG for top languages card.
    
    Args:
        data: User data from GitHub API
        theme: Color theme (dark/light)
        limit: Number of languages to show
        
    Returns:
        SVG string
    """
    user = data.get("user", {})
    name = user.get("name") or user.get("login", "Unknown")
    login = user.get("login", "unknown")
    
    # Get repositories
    repos = user.get("repositories", {}).get("nodes", [])
    
    # Calculate language stats
    language_stats = calculate_language_stats(repos)
    
    # Limit to top N languages
    top_languages = language_stats[:limit]
    
    if not top_languages:
        return create_error_svg("No language data available")
    
    # Get theme colors
    colors = get_theme_colors(theme)
    
    # Calculate card height based on number of languages
    bar_height = 12
    bar_spacing = 35
    header_height = 80
    footer_height = 20
    card_height = header_height + (len(top_languages) * bar_spacing) + footer_height
    
    # Start SVG
    svg_parts = [f'''<svg width="495" height="{card_height}" viewBox="0 0 495 {card_height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .header {{ font: 600 18px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['text']}; }}
    .stat-label {{ font: 400 12px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['text_secondary']}; }}
    .lang-name {{ font: 500 14px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['text']}; }}
    .lang-percent {{ font: 600 14px 'Segoe UI', Ubuntu, sans-serif; fill: {colors['text']}; }}
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(10px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes barGrow {{
      from {{ width: 0; }}
      to {{ width: var(--target-width); }}
    }}
    .header-group {{ animation: fadeIn 0.6s ease-out; }}
    .lang-item {{ animation: fadeIn 0.6s ease-out backwards; }}
    .lang-bar {{ animation: barGrow 1s ease-out backwards; }}
  </style>
  
  <!-- Background -->
  <rect width="495" height="{card_height}" fill="{colors['bg']}" rx="4.5"/>
  <rect x="0.5" y="0.5" width="494" height="{card_height - 1}" stroke="{colors['border']}" fill="none" rx="4"/>
  
  <!-- Header -->
  <g class="header-group">
    <text x="25" y="35" class="header">{name}'s Top Languages</text>
    <text x="25" y="55" class="stat-label">@{login}</text>
  </g>
  
  <!-- Languages -->''']
    
    # Generate language bars
    y_offset = header_height
    max_bar_width = 440
    
    for i, lang in enumerate(top_languages):
        lang_name = lang["name"]
        percentage = lang["percentage"]
        bar_width = (percentage / 100) * max_bar_width
        lang_color = get_language_color(lang_name)
        
        # Animation delay
        delay = 0.2 + (i * 0.1)
        
        svg_parts.append(f'''
  <g class="lang-item" style="animation-delay: {delay}s;">
    <!-- Language name and percentage -->
    <text x="25" y="{y_offset}" class="lang-name">{lang_name}</text>
    <text x="470" y="{y_offset}" class="lang-percent" text-anchor="end">{percentage:.1f}%</text>
    
    <!-- Progress bar background -->
    <rect x="25" y="{y_offset + 5}" width="{max_bar_width}" height="{bar_height}" fill="{colors['border']}" rx="6"/>
    
    <!-- Progress bar fill -->
    <rect class="lang-bar" x="25" y="{y_offset + 5}" width="{bar_width}" height="{bar_height}" fill="{lang_color}" rx="6" style="--target-width: {bar_width}px; animation-delay: {delay}s;"/>
  </g>''')
        
        y_offset += bar_spacing
    
    svg_parts.append('\n</svg>')
    
    return ''.join(svg_parts)


@router.get("/languages")
async def get_languages(
    user: str = Query(..., description="GitHub username"),
    theme: str = Query("dark", description="Theme (dark/light)"),
    limit: int = Query(5, description="Number of languages to show", ge=1, le=10),
    exclude: str = Query("", description="Comma-separated list of repos to exclude")
):
    """
    Generate top languages card.
    
    Args:
        user: GitHub username
        theme: Color theme
        limit: Number of languages to display
        exclude: Repositories to exclude (comma-separated)
        
    Returns:
        SVG image
    """
    # Check cache
    cache_key = f"languages:{user}:{theme}:{limit}:{exclude}"
    cached = cache.get(cache_key)
    if cached:
        return Response(content=cached, media_type="image/svg+xml")
    
    try:
        # Fetch data from GitHub
        data = await graphql(LANGUAGES_QUERY, {"username": user})
        
        if not data.get("user"):
            svg = create_error_svg(f"User '{user}' not found")
            return Response(content=svg, media_type="image/svg+xml")
        
        # Filter out excluded repositories
        if exclude:
            excluded_repos = [repo.strip().lower() for repo in exclude.split(",")]
            repos = data.get("user", {}).get("repositories", {}).get("nodes", [])
            filtered_repos = [
                repo for repo in repos 
                if repo.get("name", "").lower() not in excluded_repos
            ]
            data["user"]["repositories"]["nodes"] = filtered_repos
        
        # Generate SVG
        svg = generate_languages_svg(data, theme, limit)
        
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
