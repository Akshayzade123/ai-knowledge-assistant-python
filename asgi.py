"""
ASGI entry point for the AI Knowledge Assistant application.

This file allows running the application with:
    uvicorn asgi:app --reload

Or run directly:
    python asgi.py
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import the FastAPI application
from app.main import app  # noqa: E402

__all__ = ["app"]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("asgi:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
