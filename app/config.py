from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "BookStore"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./bookstore.db"

    JWT_SECRET: str = "dev-secret-change-in-prod"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    CORS_ORIGINS: list[str] = ["*"]

settings = Settings()