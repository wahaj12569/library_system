from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, String
from datetime import datetime
from sqlalchemy.orm import relationship
from database.database import Base

class Borrow(Base):
    __tablename__ = "borrows"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    request_date = Column(DateTime, default=datetime.utcnow)
    requested_borrow_date = Column(DateTime, nullable=True)
    requested_return_date = Column(DateTime, nullable=True)
    borrow_date = Column(DateTime, nullable=True)
    return_date = Column(DateTime, nullable=True)
    status = Column(String, default="pending")  # pending, approved, rejected, returned
    is_returned = Column(Boolean, default=False)

    book = relationship("Book")
    user = relationship("User")
