from constants import ActivityLevel, Meals, Sex, WeightLoseGoal
from datetime import date, datetime
from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Date, Enum, Float, String, Integer, ForeignKey, DateTime

# Define the Users model for the database
class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(35))
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(default=True)

    profile: Mapped["UserProfile"] = relationship(back_populates="user", uselist=False)
    food_logs: Mapped[list["FoodLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    refresh_token: Mapped[list["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    profile_picture_url: Mapped[str|None] = mapped_column(String(200))
    age: Mapped[date|None] = mapped_column(Date)
    sex: Mapped[Sex|None] = mapped_column(Enum(Sex))
    height: Mapped[float|None] = mapped_column(Float)
    start_weight: Mapped[float|None] = mapped_column(Float)
    goal_weight: Mapped[float|None] = mapped_column(Float)
    weight_loss_goal: Mapped[WeightLoseGoal|None] = mapped_column(Enum(WeightLoseGoal))
    target_date: Mapped[date|None] = mapped_column(Date)
    activity_level: Mapped[ActivityLevel|None] = mapped_column(Enum(ActivityLevel))

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    user: Mapped["Users"] = relationship(back_populates="profile")

class FoodLog(Base):
    __tablename__ = "food_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    date: Mapped[datetime] = mapped_column(DateTime)
    food_name: Mapped[str] = mapped_column(String(100))
    meal_type: Mapped[Meals] = mapped_column(Enum(Meals))
    serving_size: Mapped[float] = mapped_column(Float)
    number_of_servings: Mapped[float] = mapped_column(Float)
    calories: Mapped[float] = mapped_column(Float)
    protein: Mapped[float] = mapped_column(Float)
    carbs: Mapped[float] = mapped_column(Float)
    fat: Mapped[float] = mapped_column(Float)
    sugar: Mapped[float] = mapped_column(Float)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    user: Mapped["Users"] = relationship(back_populates="food_logs")


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    token_expiry: Mapped[datetime] = mapped_column(DateTime)
    token: Mapped[str] = mapped_column(String(280))
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    user: Mapped["Users"] = relationship(back_populates="refresh_token")