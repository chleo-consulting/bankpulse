from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql://bankpulse:bankpulse@localhost:5432/bankpulse"
    DATABASE_TEST_URL: str = "postgresql://bankpulse:bankpulse@localhost:5433/bankpulse_test"
    SECRET_KEY: str = "change-me-generate-a-real-secret-key"
    APP_NAME: str = "BankPulse Engine"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    RESEND_API_KEY: str = ""
    FRONTEND_URL: str = "http://localhost:3000"
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30
    SHARE_INVITATION_EXPIRE_DAYS: int = 7

    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


settings = Settings()
