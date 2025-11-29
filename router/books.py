from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database.database import SessionLocal
from models.books import Book

router = APIRouter(prefix="/books", tags=["Books"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_books(db: Session = Depends(get_db)):
    return db.query(Book).all()

@router.get("/{book_id}")
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Not found")
    return book

@router.get("/search")
def search_books(query: str, db: Session = Depends(get_db)):
    return db.query(Book).filter(Book.title.ilike(f"%{query}%")).all()

@router.get("/{book_id}/read")
def read_online(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    return FileResponse(book.file_path)

@router.get("/{book_id}/download")
def download_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    return FileResponse(book.file_path, filename=f"{book.title}.pdf")

@router.get("/categories")
def categories(db: Session = Depends(get_db)):
    raw = db.query(Book.category).distinct().all()
    return [c[0] for c in raw]
