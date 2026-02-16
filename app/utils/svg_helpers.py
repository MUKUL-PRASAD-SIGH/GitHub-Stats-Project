"""SVG generation utilities."""
from typing import Optional


def create_svg_response(content: str, width: int = 495, height: int = 195) -> str:
    """
    Wrap SVG content in proper SVG tags with responsive settings.
    
    Args:
        content: Inner SVG content
        width: SVG width
        height: SVG height
        
    Returns:
        Complete SVG string
    """
    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" 
                fill="none" xmlns="http://www.w3.org/2000/svg">
{content}
</svg>'''


def create_error_svg(message: str, width: int = 495, height: int = 195) -> str:
    """
    Create an error SVG with a friendly message.
    
    Args:
        message: Error message to display
        width: SVG width
        height: SVG height
        
    Returns:
        Error SVG string
    """
    content = f'''
    <rect width="{width}" height="{height}" fill="#1a1b27" rx="4.5"/>
    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" 
          fill="#ff6b6b" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="14">
        ⚠️ {message}
    </text>
    '''
    return create_svg_response(content, width, height)


def get_theme_colors(theme: str = "dark") -> dict[str, str]:
    """
    Get color scheme for a theme.
    
    Args:
        theme: Theme name (dark, light, etc.)
        
    Returns:
        Dictionary of color values
    """
    themes = {
        "dark": {
            "bg": "#1a1b27",
            "border": "#2d3748",
            "primary": "#fe428e",
            "secondary": "#a991f7",
            "text": "#ffffff",
            "text_secondary": "#9ca3af"
        },
        "light": {
            "bg": "#ffffff",
            "border": "#e5e7eb",
            "primary": "#0969da",
            "secondary": "#8250df",
            "text": "#1f2328",
            "text_secondary": "#656d76"
        }
    }
    
    return themes.get(theme, themes["dark"])
