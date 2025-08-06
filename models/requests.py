from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class UserRegistrationRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username between 3-50 characters")
    email: str = Field(..., max_length=255, description="Valid email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password between 8-128 characters")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        return v.strip()
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        # Ensure password has minimum complexity
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v

class UserLoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return v.lower().strip()

class DeleteCaptionsRequest(BaseModel):
    user_id: int = Field(..., gt=0, description="Valid user ID")