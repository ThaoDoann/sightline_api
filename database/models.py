from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, DateTime, MetaData, Table
from datetime import datetime
from config.settings import DATABASE_URL

metadata = MetaData()

captions = Table(
    "captions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("caption", String, nullable=False),
    Column("image_data", LargeBinary, nullable=False),
    Column("timestamp", DateTime, default=datetime.utcnow),
)

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),
    Column("email", String, unique=True, nullable=False),
    Column("hashed_password", String, nullable=False)
)

engine = create_engine(DATABASE_URL)

# Create all database tables
def create_tables():
    metadata.create_all(engine)