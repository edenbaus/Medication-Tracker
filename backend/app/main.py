from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings
from app.api.v1 import auth, medications, tags, admin, logs, third_parties, regimens, side_effects, symptoms, journey, dashboard

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# Add SessionMiddleware for OAuth (must be added before other middleware)
# Use SESSION_SECRET_KEY if provided, otherwise fall back to SECRET_KEY
session_secret = settings.SESSION_SECRET_KEY or settings.SECRET_KEY
app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret,
    session_cookie="medtrack_session",
    max_age=3600,  # 1 hour
    same_site="lax",
    https_only=False  # Set to True in production with HTTPS
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(medications.router, prefix="/api/medications", tags=["Medications"])
app.include_router(tags.router, prefix="/api/tags", tags=["Tags"])
app.include_router(logs.router, prefix="/api/logs", tags=["Medication Logs"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(third_parties.router, prefix="/api/third-parties", tags=["Third Parties"])
app.include_router(regimens.router, prefix="/api/regimens", tags=["Regimens"])
app.include_router(side_effects.router, prefix="/api/side-effects", tags=["Side Effects"])
app.include_router(symptoms.router, prefix="/api/symptoms", tags=["Symptoms"])
app.include_router(journey.router, prefix="/api/journey", tags=["Journey & Analytics"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Medication Tracker API",
        "version": settings.VERSION,
        "docs": "/docs"
    }
