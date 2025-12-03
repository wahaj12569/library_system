from sqlalchemy import Column, Integer, String, Boolean
from database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String(255))
    is_admin = Column(Boolean, default=False)
