"""Configuration for credit-risk-engine."""
# Support both pydantic v1 and v2 (pydantic v2 moved BaseSettings to pydantic-settings)
try:
    from pydantic_settings import BaseSettings
except Exception:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "credit-risk-engine"
    DEBUG: bool = True


settings = Settings()
SERVICE_NAME = "Internal Credit Risk Engine"
VERSION = "1.0.0"
