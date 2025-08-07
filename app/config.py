from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'what-the-fix'
    debug: bool = True
    api_version: str = 'v1'
    database_url: str
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    class Config:
        env_file = ".env"

settings = Settings()