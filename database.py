from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from settings import settings

#create an async engine for the database
engine = create_async_engine(settings.DATABASE_URL, echo=True)

#Creates a feactory for creating async sessions to interact with the database
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

#create a dependency to get the database session
async def get_db():
    async with SessionLocal() as session:
        yield session

#creates a base class for defining the models
class Base(DeclarativeBase):
    pass

