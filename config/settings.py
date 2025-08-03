import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# CORS Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")

# Model Configuration
MODEL_NAME = os.getenv("MODEL_NAME")
MAX_CAPTION_LENGTH = int(os.getenv("MAX_CAPTION_LENGTH"))

# Server Configuration
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT")