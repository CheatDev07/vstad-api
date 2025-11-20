from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database Configuration
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "vstad25!@$"
    DB_HOST: str = "vstad-db"
    DB_PORT: int = 3623
    DB_NAME: str = "video_upload_db"
    
    # MinIO Configuration
    MINIO_ENDPOINT: str = "minio:3940"  # Updated default endpoint to use minio service name for Docker compatibility
    MINIO_EXTERNAL_ENDPOINT: str = "localhost:3940"  # Added external endpoint 
    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "miniovstad"
    MINIO_BUCKET_NAME: str = "videos"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "miniovstad"
    
    # JWT Configuration
    SECRET_KEY: str = "verysecure"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 129600
    
    # Application Configuration
    DEBUG: bool = False
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 3167
    
    # Video Configuration
    ALLOWED_VIDEO_FORMATS: List[str] = ["mp4", "avi", "mov", "mkv", "webm", "flv"]
    MAX_VIDEO_SIZE_MB: int=524288000
    MAX_IMAGE_SIZE: int=524288000

    # Files Configuration
    ALLOWED_IMAGE_FORMATS: List[str] = ["jpg", "jpeg", "png"]
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://postgres:postgres@vstad-db:3623/video_upload_db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()