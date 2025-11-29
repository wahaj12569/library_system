from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.database import Base
from models.books import Base

class Borrow(Base):
    __tablename__ = "borrows"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    is_returned = Column(Boolean, default=False)

    book = relationship("Book")
