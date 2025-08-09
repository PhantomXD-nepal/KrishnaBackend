from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    SQLALCHEMY_DATABASE_URI: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_SERVER: str = 'smtp.gmail.com'
    MAIL_PORT: int = 587
    MAIL_USE_TLS: bool = True
    USE_EMAIL_VERIFICATION: bool = True
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()
