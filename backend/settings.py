from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SUPABASE_URL: str | None = None
    SUPABASE_ANON_KEY: str | None = None

    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # loads from environment
