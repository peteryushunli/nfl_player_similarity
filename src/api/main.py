"""
FastAPI application entry point for NFL Player Similarity API.

This is the main file that creates and configures the FastAPI app.
It sets up:
- CORS middleware (allows the React frontend to call the API)
- API routers (groups of related endpoints)
- Health check endpoint

To run the server:
    uvicorn src.api.main:app --reload --port 8000

The API will be available at:
    http://localhost:8000

API documentation (auto-generated):
    http://localhost:8000/docs
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.routers import players, similarity

# Create the FastAPI application
app = FastAPI(
    title="NFL Player Similarity API",
    description="Find NFL players with similar career trajectories based on statistical profiles and draft capital.",
    version="1.0.0",
    # These show up in the auto-generated docs
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS (Cross-Origin Resource Sharing)
# This is necessary for the React frontend to call the API
# In production, you'd want to restrict the origins to your actual domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default dev server
        "http://localhost:5174",  # Vite alternate port
        "http://localhost:5175",  # Vite alternate port
        "http://localhost:5176",  # Vite alternate port
        "http://localhost:3000",  # Alternative React port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5176",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include the routers
# The prefix adds a path prefix to all routes in that router
# The tags are used to group endpoints in the API docs
app.include_router(
    players.router,
    prefix="/api/v1/players",
    tags=["players"]
)

app.include_router(
    similarity.router,
    prefix="/api/v1/similarity",
    tags=["similarity"]
)


@app.get("/health", tags=["system"])
def health_check():
    """
    Health check endpoint.

    Used to verify the API is running.
    Returns a simple status message.
    """
    return {"status": "healthy"}


@app.get("/api", tags=["system"])
def api_info():
    """
    API info endpoint.

    Returns basic info about the API and links to documentation.
    """
    return {
        "name": "NFL Player Similarity API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Serve React frontend from web/dist
# This must be AFTER all API routes
frontend_path = Path(__file__).parent.parent.parent / "web" / "dist"
if frontend_path.exists():
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=frontend_path / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve the React frontend for all non-API routes."""
        return FileResponse(frontend_path / "index.html")
