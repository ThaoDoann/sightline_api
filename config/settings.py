import os

# Security Configuration
SECRET_KEY = "uVbO3B0qRr8O0E6XyVuzh7rW1KUcrObpiOOWSSZkgn4="  # Replace with a secure secret in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Database Configuration
DATABASE_URL = "sqlite:///./captions.db"

# CORS Configuration
ALLOWED_ORIGINS = ["*"]  # In production, replace with specific origins

# Model Configuration
MODEL_NAME = "Salesforce/blip-image-captioning-base"
MAX_CAPTION_LENGTH = 50

# Server Configuration
HOST = "0.0.0.0"
PORT = 8000