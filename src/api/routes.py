# src/api/routes.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Norwegian Hockey Backend")

# Add CORS at the main app level
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from src.api.claude_routes import router as claude_router
from src.api.hockey_routes import router as hockey_router  # Uncomment this

# Include routers with prefixes
app.include_router(claude_router, prefix="/ai", tags=["AI"])
app.include_router(hockey_router, prefix="/hockey", tags=["Hockey"])  # Uncomment this

@app.get("/")
async def root():
    return {
        "message": "Norwegian Hockey Backend",
        "endpoints": {
            "ai": "/ai/api/query",
            "hockey": "/hockey/teams, /hockey/players, /hockey/insights",
            "swagger": "/docs"
        }
    }

# Add this to make it runnable
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)