from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Settings

Base = declarative_base()

SQL_DB_URL = Settings().database_url
engine = create_engine(SQL_DB_URL)

# FIX: Renamed sessionlocal -> SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
