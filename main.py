import uvicorn
from fastapi import FastAPI
from auth import auth
from users import protected
from database import Base, engine
from contextlib import asynccontextmanager

# Main application setup with lifespan for database initialization and cleanup
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    
 # Initialize FastAPI app and include authentication routes   
app = FastAPI(lifespan=lifespan)
app.include_router(auth)
app.include_router(protected)

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)