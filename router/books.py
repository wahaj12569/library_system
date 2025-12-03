from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database.database import get_db
from models.books import Book
from models.user import User
from schema.book import BookCreate, BookResponse
from router.auth import get_current_user

router = APIRouter(prefix="/books", tags=["Books"])


# Create book admin api
@router.post("/", status_code=201)
def create_book(data: BookCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin can create books")
    
    #Create new book entry
    new_book = Book(
        title=data.title,
        author=data.author,
        description=data.description,
        category=data.category,
        file_path=data.file_path,
        total_copies=data.total_copies,
        available_copies=data.available_copies

    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return BookResponse(
        id=new_book.id,
        title=new_book.title,
        author=new_book.author
        )



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
