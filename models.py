from datetime import date
from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Date, Float, String, Integer, ForeignKey

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

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    profile_picture_url: Mapped[str|None] = mapped_column(String(200))
    age: Mapped[date|None] = mapped_column(Date)
    height: Mapped[float|None] = mapped_column(Float)
    start_weight: Mapped[float|None] = mapped_column(Float)
    goal_weight: Mapped[float|None] = mapped_column(Float)
    target_date: Mapped[date|None] = mapped_column(Date)
    activity_level: Mapped[str|None] = mapped_column(String(50))

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    user: Mapped["Users"] = relationship(back_populates="profile")