import os
from pydantic import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DEV_ENV = "dev"
    environment: str = DEV_ENV
    title: str
    version: str
    port: int = 5000
    db_path: str

    class Config:
        BASE_DIR = os.path.dirname(os.path.abspath("../.env"))
        env_file = os.path.join(BASE_DIR, ".env")


@lru_cache()
def get_settings():
    return Settings()
