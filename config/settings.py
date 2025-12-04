from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

load_dotenv()

class Settings(BaseSettings):
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-pro-latest", env="GEMINI_MODEL")
    
    vera_api_key: str = Field(..., env="VERA_API_KEY")
    vera_api_url: str = Field(..., env="VERA_API_URL")
    
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    max_file_size_mb: int = Field(default=20, env="MAX_FILE_SIZE_MB")
    max_image_size_mb: int = Field(default=10, env="MAX_IMAGE_SIZE_MB")
    max_video_size_mb: int = Field(default=50, env="MAX_VIDEO_SIZE_MB")
    max_audio_size_mb: int = Field(default=10, env="MAX_AUDIO_SIZE_MB")
    temp_download_path: Path = Field(default=Path("./temp_downloads"), env="TEMP_DOWNLOAD_PATH")
    
    gemini_timeout: int = 120
    vera_timeout: int = 60
    telegram_download_timeout: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
settings.temp_download_path.mkdir(exist_ok=True, parents=True)