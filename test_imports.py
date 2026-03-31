import time

def timed_import(module_name):
    start = time.time()
    try:
        print(f"Importing {module_name}...", end="", flush=True)
        __import__(module_name)
        print(f" OK ({time.time() - start:.2f}s)")
    except Exception as e:
        print(f" FAILED ({time.time() - start:.2f}s) - {e}")

timed_import("fastapi")
timed_import("pydantic")
timed_import("pymongo")
timed_import("langchain_core.messages")
timed_import("langchain_google_genai")
timed_import("langchain_ollama")
timed_import("langchain_openrouter")
timed_import("backend.db")
timed_import("backend.embedder")
timed_import("backend.ingestion_ticket")
timed_import("backend.opencode_orchestrator")
timed_import("backend.api")
