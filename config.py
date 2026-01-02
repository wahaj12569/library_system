
from dotenv import load_dotenv
import os
load_dotenv()

class Settings:
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_NAME: str = os.getenv("DB_NAME")
    NEON_DB_URL: str = os.getenv("NEON_DB_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    @property
    def database_url(self) -> str:
        # Use Neon DB if NEON_DB_URL is set
        if self.NEON_DB_URL:
            # Remove the 'psql ' prefix and surrounding quotes
            url = self.NEON_DB_URL.replace("psql ", "").strip()
            # Remove surrounding single quotes if present
            url = url.strip("'\"")
            # Convert postgresql:// to postgresql+psycopg2:// for SQLAlchemy
            if url.startswith("postgresql://"):
                return url.replace("postgresql://", "postgresql+psycopg2://", 1)
            return url
        elif self.DB_HOST:
            return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            return "sqlite:///./library.db"


settings =Settings()