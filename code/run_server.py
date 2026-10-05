"""
@file run_server.py
@description Launcher script for the FastAPI backend REST server
@module code
"""

import uvicorn

if __name__ == "__main__":
    print("Starting Orto FastAPI Server on http://0.0.0.0:8000 ...")
    uvicorn.run("backend.server:app", host="0.0.0.0", port=8000, reload=False)
