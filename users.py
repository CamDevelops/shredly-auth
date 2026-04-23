from fastapi import Depends,APIRouter, HTTPException
from models import UserProfile
from schemas import EditUserProfile, UserProfileCreate, UserProfileResponse
from database import get_db, AsyncSession
from sqlalchemy import select
from security import get_current_user


protected = APIRouter( prefix="/users", tags=["users"], dependencies=[Depends(get_current_user)])

# Endpoint to create user profile
@protected.post("/profile", status_code=201, response_model=UserProfileResponse)
async def create_profile(profile: UserProfileCreate, user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_result = await db.execute(select(UserProfile).filter(UserProfile.user_id == user.id))
    existing_user = db_result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="User profile is already created")

    profile_setup = UserProfile(
        profile_picture_url=profile.profile_picture_url,
        age=profile.age,
        height=profile.height,
        start_weight=profile.start_weight,
        goal_weight=profile.goal_weight,
        target_date=profile.target_date,
        activity_level=profile.activity_level,
        user_id=user.id
    )

    db.add(profile_setup)
    await db.commit()
    return {
        "name": user.name,
        "email": user.email,
        "username": user.username,
        "profile_picture_url": profile_setup.profile_picture_url,
        "age": profile_setup.age,
        "height": profile_setup.height,
        "start_weight": profile_setup.start_weight,
        "goal_weight": profile_setup.goal_weight,
        "target_date": profile_setup.target_date,
        "activity_level": profile_setup.activity_level   
    }

# Endpoint to edit user profile
@protected.patch("/profile", status_code=200, response_model=UserProfileResponse)
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
    return {
        "name": user.name,
        "email": user.email,
        "username": user.username,
        "profile_picture_url": existing_profile.profile_picture_url,
        "age": existing_profile.age,
        "height": existing_profile.height,
        "start_weight": existing_profile.start_weight,
        "goal_weight": existing_profile.goal_weight,
        "target_date": existing_profile.target_date,
        "activity_level": existing_profile.activity_level
    }
