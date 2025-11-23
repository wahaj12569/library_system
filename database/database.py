from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base ,DeclarativeMeta
from sqlalchemy.orm import sessionmaker
from config import Settings

Base = declarative_base()

SQL_DB_URL = Settings().database_url
engine = create_engine(SQL_DB_URL)
sessionlocal = sessionmaker(autocommit =False,autoflush=False,bind=engine)



def get_db():
    db =sessionlocal()
    try:
        yield db
    finally:
        db.close()

