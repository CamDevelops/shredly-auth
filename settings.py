from pydantic import SecretStr
from pydantic_settings import BaseSettings

'''This file contains the settings for the application. It uses pydantic to load the settings from a .env file. The settings are defined as a class that inherits from BaseSettings, and the fields are defined as class variables. The Config class is used to specify the location of the .env file. The settings are then instantiated and can be imported and used in other parts of the application.'''

class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    DATABASE_URL: str
    SECRET_KEY: SecretStr
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    RESEND_API_KEY: SecretStr

settings = Settings()