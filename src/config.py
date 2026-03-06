from pydantic_settings import BaseSettings

class Setting(BaseSettings):
    CLOUDINARY_API_SECRET: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_CLOUD_NAME: str
    DATABASE_URL: str
    API_KEY: str
    BASE_URL: str
    GROQ_API_KEY: str
    GROQ_BASE_URL: str
    GROQ_VISION_MODEL: str
    GROQ_TEXT_MODEL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Setting()
