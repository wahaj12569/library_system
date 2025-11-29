from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import SessionLocal
from models.borrow import Borrow
from models.books import Book
from models.user import User
from router.auth import get_current_user

router = APIRouter(prefix="/borrow", tags=["Borrow"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def borrow(book_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book.available_copies <= 0:
        raise HTTPException(400, "No copies available")

    borrow = Borrow(user_id=user.id, book_id=book_id)
    book.available_copies -= 1

    db.add(borrow)
    db.commit()
    return {"message": "Borrowed"}

@router.post("/return")
def return_book(book_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    borrow = db.query(Borrow).filter(
        Borrow.book_id == book_id,
        Borrow.user_id == user.id,
        Borrow.is_returned == False
    ).first()

    if not borrow:
        raise HTTPException(400, "Not borrowed")

    borrow.is_returned = True
    book = db.query(Book).filter(Book.id == book_id).first()
    book.available_copies += 1

    db.commit()
    return {"message": "Returned"}

@router.get("/my")
def my_borrowed(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Borrow).filter(Borrow.user_id == user.id, Borrow.is_returned == False).all()

@router.get("/status/{book_id}")
def borrow_status(book_id: int, db: Session = Depends(get_db)):
    count = db.query(Borrow).filter(Borrow.book_id == book_id, Borrow.is_returned == False).count()
    return {"borrowed_count": count}

@router.get("/availability/{book_id}")
def book_availability(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    return {"total": book.total_copies, "available": book.available_copies}
