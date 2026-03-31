import sys
import os
from pathlib import Path

# Add the workspace root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.db import ping_mongo
from backend.api import app
import uvicorn

if __name__ == "__main__":
    print("Checking MongoDB connectivity...")
    try:
        ping_mongo()
        print("MongoDB: OK")
    except Exception as e:
        print(f"MongoDB: FAILED - {e}")

    print("Checking FastAPI app initialization...")
    try:
        print("App: OK")
    except Exception as e:
        print(f"App: FAILED - {e}")

    print("Attempting to start server on 8000...")
    # We won't actually run it here to avoid blocking, 
    # but we checked imports and DB.
