#!/usr/bin/env python3
"""
Database initialization script for Sightline API

This script will:
1. Drop existing tables if they exist
2. Create fresh tables (User, Caption)
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from database.dbmodels import metadata
from config.settings import DATABASE_URL

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize database
def init_database():
    try:
        logger.info("Starting database initialization...")
        logger.info(f"Database URL: {DATABASE_URL}")
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Drop all existing tables
        logger.info("Dropping existing tables...")
        metadata.drop_all(engine)
        logger.info("Existing tables dropped successfully!")
        
        # Create all tables with fresh schema
        logger.info("Creating tables...")
        metadata.create_all(engine)
        logger.info("Tables created successfully!")
        
        # Verify tables were created
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"Created tables: {tables}")
        
        logger.info("Database initialization completed successfully!")

        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()