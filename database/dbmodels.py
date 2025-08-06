from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, DateTime, MetaData, Table, ForeignKey
from datetime import datetime
from config.settings import DATABASE_URL

metadata = MetaData()

captions = Table(
    "Caption",
    metadata,
    Column("caption_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("User.user_id", ondelete="CASCADE"), nullable=False),
    Column("caption", String, nullable=False),
    Column("image_data", LargeBinary, nullable=False),
    Column("timestamp", DateTime, default=datetime.utcnow),
)

users = Table(
    "User",
    metadata,
    Column("user_id", Integer, primary_key=True, autoincrement=True),
    Column("username", String, unique=True, nullable=False),
    Column("email", String, unique=True, nullable=False),
    Column("hashed_password", String, nullable=False)
)

engine = create_engine(DATABASE_URL)

# Create all database tables
def create_tables():
    metadata.create_all(engine)