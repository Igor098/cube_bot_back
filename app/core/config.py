import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str = None
    DB_PORT: str = None
    DB_NAME: str = None
    DB_USER: str = None
    DB_PASSWORD: str = None
    ACCESS_EXPIRE_MINUTES: int = None
    REFRESH_EXPIRE_DAYS: int = None
    ALGORITHM: str = None
    SECRET_KEY:str = None
    JWT_ISSUER: str = None
    JWT_AUDIENCE: str = None
    JWT_CLOCK_SKEW_SECONDS: int = None
    MODE: str = None

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../", ".env")
    )

    def get_database_url(self):
        if self.MODE == "development":
            return f"sqlite+aiosqlite:///app/db/db.sqlite3"
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
