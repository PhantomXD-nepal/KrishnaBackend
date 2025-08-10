from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    EMAIL_HOST: str = 'smtp.gmail.com'
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str
    USE_EMAIL_VERIFICATION: bool = True
    ALGORITHM: str = "HS256"
    SPARROW_SMS_API_TOKEN: str
    BACKEND_CORS_ORIGINS: str

    class Config:
        env_file = ".env"

settings = Settings()