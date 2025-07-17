from fastapi import FastAPI, File, UploadFile, HTTPException,Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import io
import torch
import uvicorn
import logging
from databases import Database
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, DateTime, MetaData, Table
from datetime import datetime, timedelta
from passlib.hash import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel


SECRET_KEY = "uVbO3B0qRr8O0E6XyVuzh7rW1KUcrObpiOOWSSZkgn4="  # Replace with a secure secret in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Database setup
DATABASE_URL = "sqlite:///./captions.db"
database = Database(DATABASE_URL)
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
metadata.create_all(engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sightline API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize BLIP model
logger.info("Loading BLIP model...")
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
logger.info("BLIP model loaded successfully!")

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Pydantic Models
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    email: str

@app.get("/")
async def root():
    return {"message": "Welcome to Sightline API"}

@app.post("/register")
async def register_user(user: UserRegister):
    # Check existing
    query = users.select().where(users.c.email == user.email)
    if await database.fetch_one(query):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = bcrypt.hash(user.password)
    insert_query = users.insert().values(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    await database.execute(insert_query)
    return {"message": "User registered successfully"}

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    query = users.select().where(users.c.email == form_data.username)
    user = await database.fetch_one(query)

    if not user or not bcrypt.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user["email"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user["username"],
        "email": user["email"]
    }

@app.post("/caption")
async def generate_caption(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        inputs = processor(image, return_tensors="pt")
        outputs = model.generate(**inputs, max_length=50)
        caption_text = processor.decode(outputs[0], skip_special_tokens=True)

        query = captions.insert().values(
            caption=caption_text,
            image_data=contents,
            timestamp=datetime.utcnow()
        )
        await database.execute(query)
        return {"caption": caption_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating caption: {str(e)}")

import base64

@app.get("/captions")
async def fetch_captions(token: str = Depends(oauth2_scheme)):
    query = captions.select().order_by(captions.c.timestamp.desc())
    rows = await database.fetch_all(query)
    return [
        {
            "caption": row["caption"],
            "timestamp": row["timestamp"].isoformat(),
            "image_base64": base64.b64encode(row["image_data"]).decode("utf-8"),
        }
        for row in rows
    ]

if __name__ == "__main__":
    host = "localhost" 
    port = 8000
    logger.info(f"Starting server on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port) 