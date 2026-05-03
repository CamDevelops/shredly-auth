from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, ValidationInfo, field_validator
from constants import ActivityLevel, Meals, Sex, WeightLoseGoal
import re

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
    sex: Sex
    height: float
    start_weight: float
    goal_weight:float
    weight_loss_goal: WeightLoseGoal
    target_date: date
    activity_level: ActivityLevel
    
    @field_validator('height')
    @classmethod
    def validate_height(cls, value: float) -> float:
        if value <= 0:
            raise ValueError('Height must be positive')
        if value >= 300:
            raise ValueError('Height must be realistic (less than 300 inches)')
        return value
    
    @field_validator('start_weight')
    @classmethod
    def validate_start_weight(cls, value: float) -> float:
        if value <= 0:
            raise ValueError('Weight must be positive')
        if value >= 500:
            raise ValueError('Weight must be realistic (less than 500 kg)')
        return value
    
    @field_validator('goal_weight')
    @classmethod
    def validate_goal_weight(cls, value: float) -> float:
        if value <= 0:
            raise ValueError('Goal weight must be positive')
        if value >= 500:
            raise ValueError('Goal weight must be realistic (less than 500 kg)')
        return value
    
    @field_validator('target_date')
    @classmethod
    def validate_target_date(cls, value: date) -> date:
        if value <= date.today():
            raise ValueError('Target date must be in the future')
        return value

# UserProfileResponse model for user profile response
class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    email: EmailStr
    username: str
    profile_picture_url: str|None
    age: date
    sex: Sex|None
    height: float
    start_weight: float
    goal_weight:float
    weight_loss_goal: WeightLoseGoal|None
    target_date: date
    activity_level: ActivityLevel

# EditUserProfile model for editing user profile information
class EditUserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    profile_picture_url: str|None
    age: date|None
    sex: Sex|None
    height: float|None
    start_weight: float|None
    goal_weight:float|None
    weight_loss_goal: WeightLoseGoal|None
    target_date: date|None
    activity_level: ActivityLevel|None
    
    @field_validator('height')
    @classmethod
    def validate_height(cls, value: float|None) -> float|None:
        if value is not None:
            if value <= 0:
                raise ValueError('Height must be positive')
            if value >= 300:
                raise ValueError('Height must be realistic (less than 300 inches)')
        return value
    
    @field_validator('start_weight')
    @classmethod
    def validate_start_weight(cls, value: float|None) -> float|None:
        if value is not None:
            if value <= 0:
                raise ValueError('Weight must be positive')
            if value >= 500:
                raise ValueError('Weight must be realistic (less than 500 kg)')
        return value
    
    @field_validator('goal_weight')
    @classmethod
    def validate_goal_weight(cls, value: float|None) -> float|None:
        if value is not None:
            if value <= 0:
                raise ValueError('Goal weight must be positive')
            if value >= 500:
                raise ValueError('Goal weight must be realistic (less than 500 kg)')
        return value
    
    @field_validator('target_date')
    @classmethod
    def validate_target_date(cls, value: date|None) -> date|None:
        if value is not None and value <= date.today():
            raise ValueError('Target date must be in the future')
        return value

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
    
class LogFood(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: datetime
    food_name: str
    meal_type: Meals
    serving_size: float
    number_of_servings: float
    calories: float
    protein: float
    carbs: float
    fat: float
    sugar: float

    @field_validator('serving_size')
    @classmethod
    def validate_serving_size(cls, value: str|float) -> float:
        # Convert to float if string
        if isinstance(value, str):
            numeric_value = re.sub(r'[^0-9.]', '', value)
            final_float = float(numeric_value)
        else:
            final_float = value
        
        # Validate that it's positive
        if final_float <= 0:
            raise ValueError('Serving size must be greater than zero')
        return final_float
    
    @field_validator('date')
    @classmethod
    def validate_date_not_future(cls, value: datetime) -> datetime:
        if value > datetime.now():
            raise ValueError('Date cannot be in the future')
        return value
    
    @field_validator('calories')
    @classmethod
    def validate_calories_non_negative(cls, value: float) -> float:
        if value < 0:
            raise ValueError('Calories cannot be negative')
        return value
    
class FoodLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: datetime
    food_name: str
    meal_type: Meals
    serving_size: float
    number_of_servings: float
    calories: float
    protein: float
    carbs: float
    fat: float
    sugar: float


class EditFoodEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: datetime|None
    food_name: str|None
    meal_type: Meals|None
    serving_size: float|None
    number_of_servings: float|None
    calories: float|None
    protein: float|None
    carbs: float|None
    fat: float|None
    sugar: float|None
    
    @field_validator('date')
    @classmethod
    def validate_date_not_future(cls, value: datetime|None) -> datetime|None:
        if value is not None and value > datetime.now():
            raise ValueError('Date cannot be in the future')
        return value
    
    @field_validator('calories')
    @classmethod
    def validate_calories_non_negative(cls, value: float|None) -> float|None:
        if value is not None and value < 0:
            raise ValueError('Calories cannot be negative')
        return value
    
    @field_validator('serving_size')
    @classmethod
    def validate_serving_size_positive(cls, value: float|None) -> float|None:
        if value is not None and value <= 0:
            raise ValueError('Serving size must be greater than zero')
        return value

class DashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    daily_calories: float
    calories_consumed: float
    calories_remaining: float
    protein_consumed: float
    carbs_consumed: float
    fat_consumed: float
    sugar_consumed: float
    meals: list[FoodLogResponse]
