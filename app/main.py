"""
This script initializes and runs a FastAPI application.
"""

from dotenv import load_dotenv
from app.bootstrap.app_factory import create_app

load_dotenv()

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
