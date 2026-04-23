from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, ValidationInfo, field_validator

# CreateUser model for user registration
class CreateUser(BaseModel):
    name: str
    email: EmailStr
    username: str
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str) -> str: 
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isupper() for char in value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in value):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char.isdigit() for char in value):
            raise ValueError('Password must contain at least one digit')
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for char in value):
            raise ValueError('Password must contain at least one special character')
        return value
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError('Username must be at least 8 characters long')
        return value
    
# UserResponse model for user response, excluding password
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    email: EmailStr
    name: str

# UserProfile model for user profile information
class UserProfileCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    profile_picture_url: str|None
    age: date
    height: float
    start_weight: float
    goal_weight:float
    target_date: date
    activity_level: str

# UserProfileResponse model for user profile response
class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    email: EmailStr
    username: str
    profile_picture_url: str|None
    age: date
    height: float
    start_weight: float
    goal_weight:float
    target_date: date
    activity_level: str

# EditUserProfile model for editing user profile information
class EditUserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    profile_picture_url: str|None
    age: date|None
    height: float|None
    start_weight: float|None
    goal_weight:float|None
    target_date: date|None
    activity_level: str|None

# Token model for JWT token response
class Token(BaseModel):
    access_token: str
    token_type: str

# EmailSchema model for sending emails
class EmailSchema(BaseModel):
    to: list[EmailStr]
    subject: str
    html: str

# ForgotPassword model for requesting password reset
class ForgotPassword(BaseModel):
    email: EmailStr

# ResetPassword model for resetting password, including validation for new password and confirm password
class ResetPassword(BaseModel):
    new_password: str
    confirm_password: str

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isupper() for char in value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in value):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char.isdigit() for char in value):
            raise ValueError('Password must contain at least one digit')
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for char in value):
            raise ValueError('Password must contain at least one special character')
        return value
    
    @field_validator('confirm_password')
    @classmethod
    def validate_confirm_password(cls, value: str, info: ValidationInfo) -> str:
        if 'new_password' in info.data and value != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return value