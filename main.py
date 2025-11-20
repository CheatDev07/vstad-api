from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from database import engine, Base
from routes import auth_router, videos_router, interactions_router, admin_router, playlists_router, profile_router
from config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Application shutdown")

# Create FastAPI app
app = FastAPI(
    title="VSTAD API",
    version="1",
    description="FastAPI with MinIO Storage",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(videos_router)
app.include_router(interactions_router)
app.include_router(admin_router)
app.include_router(playlists_router)


# # Health check endpoint
# @app.get("/health")
# def health_check():
#     return {"status": "healthy"}

# # Root endpoint
# @app.get("/")
# def root():
#     return {
#         "message": "VSTAD API",
#         "version": "1",
#         "docs": "/docs",
#         "redoc": "/redoc"
#     }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
