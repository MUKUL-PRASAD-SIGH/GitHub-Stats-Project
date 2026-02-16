"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.responses import Response
from .config import settings
from .endpoints import stats, streak, languages, trophy, heatmap, snake

app = FastAPI(
    title="GitHub Profile API",
    description="Dynamic SVG badges for GitHub profiles",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Register routers
app.include_router(stats.router, tags=["stats"])
app.include_router(streak.router, tags=["streak"])
app.include_router(languages.router, tags=["languages"])
app.include_router(trophy.router, tags=["trophy"])
app.include_router(heatmap.router, tags=["heatmap"])
app.include_router(snake.router, tags=["snake"])


@app.get("/")
async def root():
    """API homepage with usage instructions."""
    return {
        "name": "GitHub Profile API",
        "version": "1.0.0",
        "endpoints": {
            "/stats": "User statistics card",
            "/streak": "Contribution streak",
            "/languages": "Top languages chart",
            "/heatmap": "Contribution heatmap",
            "/trophy": "Achievement trophies",
            "/snake": "Contribution snake animation"
        },
        "usage": "Add ?user=USERNAME to any endpoint",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
