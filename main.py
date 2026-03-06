from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import router as complaint_router
from src.database import init_db

app = FastAPI(
    title="Civic Lens API",
    description="API for AI-Powered Civic Grievance Reporting System",
    version="1.0.0",
)

# Initialize database
init_db()

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(complaint_router)


@app.get("/")
def health_check():
    return {"status": "System Operational.", "service": "Civic Lens API"}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }
