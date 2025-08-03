from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from models.user import User
from auth.jwt_handler import create_access_token
from database.connection import get_database
from database.dbmodels import users

router = APIRouter()

# Endpoint to register a new user
@router.post("/register")
async def register_user(user: User):
    database = await get_database()
    
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


# Endpoint to login user and return access token
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    database = await get_database()
    query = users.select().where(users.c.email == form_data.username)
    user = await database.fetch_one(query)

    if not user or not bcrypt.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user["email"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user["user_id"],
        "username": user["username"],
        "email": user["email"]
    }