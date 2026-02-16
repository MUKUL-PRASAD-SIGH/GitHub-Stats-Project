"""GitHub GraphQL API client."""
import httpx
from typing import Any, Optional
from .config import settings


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""
    pass


class RateLimitError(GitHubAPIError):
    """Raised when GitHub API rate limit is exceeded."""
    pass


async def graphql(query: str, variables: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """
    Execute a GraphQL query against GitHub API.
    
    Args:
        query: GraphQL query string
        variables: Optional query variables
        
    Returns:
        GraphQL response data
        
    Raises:
        RateLimitError: When rate limit is exceeded
        GitHubAPIError: For other API errors
    """
    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {settings.github_token}",
        "Content-Type": "application/json",
    }
    
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for GraphQL errors
            if "errors" in data:
                error_msg = data["errors"][0].get("message", "Unknown error")
                
                # Check if it's a rate limit error
                if "rate limit" in error_msg.lower():
                    raise RateLimitError(error_msg)
                
                raise GitHubAPIError(error_msg)
            
            return data.get("data", {})
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                raise RateLimitError("GitHub API rate limit exceeded")
            raise GitHubAPIError(f"HTTP {e.response.status_code}: {e.response.text}")
        
        except httpx.RequestError as e:
            raise GitHubAPIError(f"Request failed: {str(e)}")
