import uvicorn
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import connect_database, disconnect_database
from routers import auth, captions
from config.settings import ALLOWED_ORIGINS, HOST, PORT, API_VERSION

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Lifespan manager to handle database connection 
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_database()
    logger.info("Database connected")
    yield
    # Shutdown
    await disconnect_database()
    logger.info("Database disconnected")

app = FastAPI(
    title="Sightline API",
    description="AI-powered image captioning service with user management",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with configurable API versioning
api_prefix = f"/api/{API_VERSION}"
app.include_router(auth.router, prefix=api_prefix, tags=["Authentication"])
app.include_router(captions.router, prefix=api_prefix, tags=["Captions"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Welcome to Sightline API",
        "api_version": API_VERSION,
    }


if __name__ == "__main__":
    logger.info(f"Starting server on http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)