"""
FastAPI Backend for Flyto2 UI Builder
Provides metadata API for dynamic form generation

Note: Run this app from project root using start_api_server.py
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.ui.web.backend.api.modules_metadata import router as modules_router

# Create FastAPI app
app = FastAPI(
    title="Flyto2 API",
    description="Workflow automation engine API - provides module metadata for UI builder",
    version="1.0.0"
)

# CORS middleware (allow frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(modules_router)


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Flyto2 API",
        "version": "1.0.0",
        "description": "Workflow automation engine - module metadata API",
        "endpoints": {
            "modules": "/api/modules/list",
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("🚀 Starting Flyto2 API Server")
    print("=" * 70)
    print(f"   API Docs: http://localhost:8000/docs")
    print(f"   Modules API: http://localhost:8000/api/modules/list")
    print("=" * 70)

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
