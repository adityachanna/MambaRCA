import sys
from pathlib import Path

# Add the workspace root to sys.path
sys.path.insert(0, str(Path(__file__).parent))

print("Importing backend.api...")
from backend.api import app
print("Import successful!")

# Manually trigger startup events
import asyncio
from fastapi.testclient import TestClient

async def run_startup():
    print("Running startup events...")
    # This is how you trigger startup events in code
    for handler in app.router.on_startup:
        if asyncio.iscoroutinefunction(handler):
            await handler()
        else:
            handler()
    print("Startup events completed!")

if __name__ == "__main__":
    asyncio.run(run_startup())
