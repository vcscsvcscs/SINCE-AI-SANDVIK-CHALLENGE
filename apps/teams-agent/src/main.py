"""Main entry point for the application"""
import uvicorn
from os import environ
from .start_server import app

# Use "0.0.0.0" to bind to all interfaces (required for Docker containers)
# Use "localhost" only if explicitly set via HOST environment variable
host = environ.get("HOST", "0.0.0.0")
port = int(environ.get("PORT", 3978))
    
uvicorn.run(app, host=host, port=port)
