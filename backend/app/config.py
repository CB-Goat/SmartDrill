from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "智练通"
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    database_url: str = "mysql+pymysql://root:password@localhost:3306/smartdrill"
    
    upload_dir: str = "/app/uploads"
    
    class Config:
        env_file = ".env"

settings = Settings()