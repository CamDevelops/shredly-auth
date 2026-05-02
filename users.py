from fastapi import Depends,APIRouter, HTTPException
from models import UserProfile, FoodLog
from schemas import EditUserProfile, UserProfileCreate, UserProfileResponse, DashboardResponse,FoodLogResponse
from database import get_db, AsyncSession
from sqlalchemy import select, func
from security import get_current_user
from helpers import profile_response, calculate_calories, calculate_age
from datetime import date


protected = APIRouter( prefix="/users", tags=["users"], dependencies=[Depends(get_current_user)])

# Endpoint to create user profile
@protected.post("/create_profile", status_code=201, response_model=UserProfileResponse)
async def create_profile(profile: UserProfileCreate, user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_result = await db.execute(select(UserProfile).filter(UserProfile.user_id == user.id))
    existing_user = db_result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="User profile is already created")

    profile_setup = UserProfile(
        profile_picture_url=profile.profile_picture_url,
        age=profile.age,
        sex=profile.sex,
        height=profile.height,
        start_weight=profile.start_weight,
        goal_weight=profile.goal_weight,
        weight_loss_goal=profile.weight_loss_goal,
        target_date=profile.target_date,
        activity_level=profile.activity_level,
        user_id=user.id
    )

    db.add(profile_setup)
    await db.commit()
    return profile_response(user, profile_setup)  

# Endpoint to get user profile
@protected.get("/profile", status_code=200, response_model=UserProfileResponse)
async def get_profile(user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = db_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile has not been created yet")
    return profile_response(user, profile)

# Endpoint to edit user profile
@protected.patch("/profile/edit", status_code=200, response_model=UserProfileResponse)
async def edit_profile(profile: EditUserProfile, user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    existing_profile = db_result.scalar_one_or_none()
    if not existing_profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    for field in profile.model_fields_set:
        if getattr(profile, field) is not None:
            setattr(existing_profile, field, getattr(profile, field))  
    await db.commit()
    await db.refresh(existing_profile)
    return profile_response(user, existing_profile)

@protected.get("/dashboard", status_code=200, response_model=DashboardResponse)
async def user_dashboard(user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = db_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="User Profile doesnt exist")
    age = calculate_age(profile.age)
    daily_calories = calculate_calories(profile.sex, profile.start_weight, profile.height, age, profile.activity_level, profile.weight_loss_goal)
    db_result = await db.execute(select(FoodLog).where(FoodLog.user_id == user.id).where(func.date(FoodLog.date) == date.today()))
    todays_food = db_result.scalars().all()
    calories_consumed = sum([entry.calories for entry in todays_food])
    remaining_calories = daily_calories - calories_consumed
    protein_consumed = sum([entry.protein for entry in todays_food])
    carbs_consumed = sum([entry.carbs for entry in todays_food])
    fats_consumed = sum([entry.fat for entry in todays_food])
    sugar_consumed = sum([entry.sugar for entry in todays_food])
    return DashboardResponse(
        daily_calories=daily_calories,
        calories_consumed=calories_consumed,
        calories_remaining=remaining_calories,
        protein_consumed=protein_consumed,
        carbs_consumed=carbs_consumed,
        fat_consumed=fats_consumed,
        sugar_consumed=sugar_consumed,
        meals=[FoodLogResponse.model_validate(item) for item in todays_food]
    )