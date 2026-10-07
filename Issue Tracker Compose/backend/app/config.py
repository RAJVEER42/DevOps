from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Overridden by the DATABASE_URL environment variable (docker-compose sets it).
    database_url: str = "postgresql+psycopg://tracker:tracker@localhost:5432/tracker"
    app_version: str = "dev"


settings = Settings()
