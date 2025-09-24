"""
Background Removal API
A FastAPI application for AI-powered background removal with auto human detection.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import API_TITLE, API_DESCRIPTION, API_VERSION, CORS_ORIGINS, CORS_CREDENTIALS, CORS_METHODS, CORS_HEADERS
from api.routes import router

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_CREDENTIALS,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)

# Include API routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)