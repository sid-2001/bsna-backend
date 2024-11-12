from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_URL : str
    JWT_SECRET_KEY: str
    JWT_ALGO: str
    HOST: str
    PORT: str
    SERVICE_KEY_FILE: str
    GOOGLE_SERVICES_FILE: str
    FIREBASE_FCM_URL: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
    
Config = Settings()