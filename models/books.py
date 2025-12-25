from sqlalchemy import Column, Integer, String
from database.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    category = Column(String)
    description = Column(String)
    picture_url = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)

