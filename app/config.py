from pydantic import BaseSettings

class Settings(BaseSettings):
    DB_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "CHANGE_ME_TO_A_SECURE_VALUE"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60*24
    OTP_EXPIRY_SECONDS: int = 300
    SMS_PROVIDER_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
