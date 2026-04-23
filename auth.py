from datetime import timedelta
from fastapi import Depends, HTTPException, APIRouter, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from database import get_db, AsyncSession
from schemas import CreateUser, ForgotPassword
from models import Users
from security import hash_password, verify_password, create_access_token
from services.email import password_reset_email

auth = APIRouter()

# User registration endpoint
@auth.post("/register", status_code=201)
async def register_user(user: CreateUser, db: AsyncSession = Depends(get_db)):
    db_results = await db.execute(select(Users).filter(or_(Users.username == user.username, Users.email == user.email)))
    user_info = db_results.scalar_one_or_none()
    if user_info:
        raise HTTPException(status_code=409, detail="The Username or email is already registered.")
    
    hashed_password = hash_password(user.password)

    new_user = Users(
        name=user.name,
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )

    db.add(new_user)
    await db.commit()
    return {"message": "User created successfully."}

# User login endpoint
@auth.post("/login", status_code=200)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    db_result = await db.execute(select(Users).filter(Users.username == form_data.username))
    user = db_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="The Username or password provided is incorrect.")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="The Username or password provided is incorrect.")
    
    return {"access_token": create_access_token({"sub": str(user.id)}), "token_type": "bearer"}

# Endpoint to send password reset email
@auth.post("/reset-password-email", status_code=200)
async def send_reset_password_email(email: ForgotPassword, background_task: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    db_result = await db.execute(select(Users).where(Users.email == email.email))
    valid_email = db_result.scalar_one_or_none()
    if not valid_email:
        raise HTTPException(status_code=404, detail="No user found with the provided email address.")
    token = create_access_token({"sub": str(valid_email.id)}, expires_delta=timedelta(minutes=30))
    reset_link = f"http://localhost:3000/reset-password?token={token}"
    background_task.add_task(password_reset_email, email, reset_link)
    return {"message": "Password reset email has been sent, check your inbox."}