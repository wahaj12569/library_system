
from dotenv import load_dotenv
import os
load_dotenv()

class Settings:
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_NAME: str = os.getenv("DB_NAME")
    SECRET_KEY:str = os.getenv("SECRET_KEY")
    ALGORITHM:str= os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES :str = os 

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings =Settings()