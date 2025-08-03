import uvicorn
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import connect_database, disconnect_database
from routers import auth, captions
from config.settings import ALLOWED_ORIGINS, HOST, PORT

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

app = FastAPI(title="Sightline API", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(captions.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Sightline API"}

if __name__ == "__main__":
    logger.info(f"Starting server on http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)