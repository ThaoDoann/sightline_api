from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from models.user import User
from models.requests import UserRegistrationRequest, UserLoginRequest
from auth.jwt_handler import create_access_token
from database.connection import get_database
from database.dbmodels import users
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Endpoint to register a new user
@router.post("/register", 
             summary="Register new user",
             description="Create a new user account with validation")
async def register_user(user_data: UserRegistrationRequest):
    try:
        database = await get_database()
        
        # Get validated inputs
        username = user_data.username
        email = user_data.email  # Already validated and sanitized by Pydantic
        
        # Check if email already exists
        query = users.select().where(users.c.email == email)
        existing_user = await database.fetch_one(query)
        if existing_user:
            logger.warning(f"Registration attempt with existing email: {email}")
            raise HTTPException(status_code=400, detail="Email already registered")

        # Check if username already exists
        query = users.select().where(users.c.username == username)
        existing_username = await database.fetch_one(query)
        if existing_username:
            logger.warning(f"Registration attempt with existing username: {username}")
            raise HTTPException(status_code=400, detail="Username already taken")

        # Hash password
        hashed_password = bcrypt.hash(user_data.password)
        
        # Insert new user
        insert_query = users.insert().values(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        await database.execute(insert_query)
        
        logger.info(f"New user registered: {email}")
        return {"message": "User registered successfully"}

    except HTTPException as e:
        raise e    
    except ValueError as e:
        logger.warning(f"Registration validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Endpoint to login user and return access token
@router.post("/login",
             summary="User login",
             description="Authenticate user and return access token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        database = await get_database()
        
        # Sanitize email input
        email = form_data.username.lower().strip()
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            logger.warning(f"Login attempt with invalid email format: {email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Get user from database
        query = users.select().where(users.c.email == email)
        user = await database.fetch_one(query)

        # Verify credentials
        if not user or not bcrypt.verify(form_data.password, user["hashed_password"]):
            logger.warning(f"Failed login attempt for email: {email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create access token
        access_token = create_access_token(data={"sub": user["email"]})
        
        logger.info(f"Successful login for user: {email}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"]
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")