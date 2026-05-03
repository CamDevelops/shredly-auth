from datetime import timedelta, datetime, timezone
from fastapi import Depends, HTTPException, APIRouter, BackgroundTasks, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from database import get_db, AsyncSession
from schemas import CreateUser, ForgotPassword, ResetPassword
from models import Users, RefreshToken
from settings import settings
import jwt
from security import hash_password, verify_password, create_access_token, refresh_token
from services.email import password_reset_email


auth = APIRouter()

# User registration endpoint
@auth.post("/register", status_code=201)
async def register_user(user: CreateUser, db: AsyncSession = Depends(get_db)):
    db_results = await db.execute(select(Users).where(or_(Users.username == user.username, Users.email == user.email)))
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
async def login_user(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    db_result = await db.execute(select(Users).where(Users.username == form_data.username))
    user = db_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="The Username or password provided is incorrect.")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="The Username or password provided is incorrect.")
    
    re_token = refresh_token({"sub": str(user.id)})
    refreshed_token = RefreshToken(
        user_id=user.id,
        token_expiry=datetime.now(timezone.utc) + timedelta(days=7),
        token=re_token
    )
    db.add(refreshed_token)
    await db.commit()
    response.set_cookie(key="refresh_token", value=re_token, httponly=True, secure=True, samesite="lax")
    return {"access_token": create_access_token({"sub": str(user.id)}), "token_type": "bearer"}

@auth.get("refresh/token")
async def refresh_access_token(request: Request, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    time = datetime.now(timezone.utc)
    db_result = await db.execute(select(RefreshToken).where(RefreshToken.token == token).where(RefreshToken.token_expiry > time))
    refreshed_token = db_result.scalar_one_or_none()
    if not refreshed_token:
        raise HTTPException(status_code=401, detail="The Token is not valid or has expired.")
    return {"access_token": create_access_token({"sub": str(refreshed_token.user_id)}), "token_type": "bearer"}

# Endpoint to send password reset email
@auth.post("/reset-password-email", status_code=200)
async def send_reset_password_email(email: ForgotPassword, background_task: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    db_result = await db.execute(select(Users).where(Users.email == email.email))
    valid_email = db_result.scalar_one_or_none()
    if not valid_email:
        raise HTTPException(status_code=404, detail="No user found with the provided email address.")
    token = create_access_token({"sub": str(valid_email.id)}, expires_delta=timedelta(minutes=30))
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    background_task.add_task(password_reset_email, email.email, reset_link)
    return {"message": "Password reset email has been sent, check your inbox."}

# Endpoint to reset password using the token sent in the email
@auth.post("/reset-password", status_code=200)
async def reset_password(token: str, password: ResetPassword, db: AsyncSession = Depends(get_db)):
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY.get_secret_value(), algorithms=["HS256"])
        db_result = await db.execute(select(Users).where(Users.id == int(decoded_token["sub"])))
        user = db_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        hashed_password = hash_password(password.new_password)
        user.hashed_password = hashed_password
        await db.commit()
        return {"message": "Password was reset Successfully."}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="reset link has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid reset link.")

@auth.delete("/logout")
async def sign_out(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    db_result = await db.execute(select(RefreshToken).where(RefreshToken.token == token))
    user_token = db_result.scalar_one_or_none()
    if not user_token:
        raise HTTPException(status_code=401, detail="User token is not found")
    db.delete(user_token)
    await db.commit()
    response.delete_cookie("refresh_token")
    return {"message": "You have been succefully signed out"}