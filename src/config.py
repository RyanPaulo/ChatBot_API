from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str

    GOOGLE_API_KEY: str
    WATCHER_TARGET_FOLDER: str


    class Config:
        env_file = ".env"

settings = Settings()
