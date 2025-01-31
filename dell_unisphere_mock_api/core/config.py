"""Configuration settings for the Dell Unisphere Mock API."""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    API_BASE_URL: str = "http://localhost:8000/api"
    PROJECT_NAME: str = "Dell Unisphere Mock API"
    VERSION: str = "1.0.0"
    CSRF_ENABLED: bool = False  # Default to False to disable CSRF

    model_config = ConfigDict(env_prefix="UNISPHERE_", case_sensitive=False)


settings = Settings()
