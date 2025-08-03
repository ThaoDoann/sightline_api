from databases import Database
from config.settings import DATABASE_URL
from .dbmodels import create_tables

database = Database(DATABASE_URL)

async def connect_database():
    await database.connect()
    create_tables() # Create tables if they don't exist

async def disconnect_database():
    await database.disconnect()

async def get_database():
    return database