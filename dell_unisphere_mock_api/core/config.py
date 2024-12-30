"""Configuration settings for the Dell Unisphere Mock API."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    API_BASE_URL: str = "http://localhost:8000/api"
    PROJECT_NAME: str = "Dell Unisphere Mock API"
    VERSION: str = "1.0.0"

    class Config:
        """Pydantic config."""

        env_prefix = "UNISPHERE_"
        case_sensitive = False


settings = Settings()
