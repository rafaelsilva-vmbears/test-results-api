#!/usr/bin/env python3

"""
Entry point script to run the FastAPI application.
Can be executed directly with `python run.py` from the project root.
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv
from app.infrastructure.logging.logging_config import initialize_logging, get_logger

from app.main import app

load_dotenv()

initialize_logging()
logger = get_logger(__name__)


def main():
    """Entry point for the FastAPI application."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)

    try:
        # Determine environment
        env = os.getenv("ENVIRONMENT", "production").lower()
        is_dev = env == "development"

        logger.info(f"Starting server in {env} mode (reload={is_dev})")

        # Use string extraction for reload support only in dev
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=is_dev,
            workers=1 if is_dev else 4 # Production optimization suggestion
        )
    except Exception as e:
        logger.error("Failed to start application: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
