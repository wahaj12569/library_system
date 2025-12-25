from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from database.database import get_db
from models.books import Book
from models.user import User
from schema.book import BookCreate, BookResponse
from router.auth import get_current_user
import os

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
        picture_url=data.picture_url,
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
        author=new_book.author,
        description=new_book.description,
        category=new_book.category,
        picture_url=new_book.picture_url,
        file_path=new_book.file_path,
        total_copies=new_book.total_copies,
        available_copies=new_book.available_copies
        )



@router.get("/")
def get_books(db: Session = Depends(get_db)):
    return db.query(Book).all()

@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin can delete books")
    
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")
    
    db.delete(book)
    db.commit()
    return {"message": "Book deleted"}

@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, data: BookCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin can update books")
    
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")
    
    book.title = data.title
    book.author = data.author
    book.description = data.description
    book.category = data.category
    book.picture_url = data.picture_url
    book.file_path = data.file_path
    book.total_copies = data.total_copies
    book.available_copies = data.available_copies
    
    db.commit()
    db.refresh(book)
    
    return book

@router.get("/search")
def search_books(query: str, db: Session = Depends(get_db)):
    return db.query(Book).filter(Book.title.ilike(f"%{query}%")).all()


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")
    return book

@router.get("/{book_id}/view")
def view_pdf(
    book_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stream PDF for inline viewing - download disabled"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")
    
    if not book.file_path:
        raise HTTPException(404, "PDF not available for this book")
    
    # Check if user has approved borrow
    from models.borrow import Borrow
    borrow = db.query(Borrow).filter(
        Borrow.user_id == current_user.id,
        Borrow.book_id == book_id,
        Borrow.status == "approved",
        Borrow.is_returned == False
    ).first()
    
    if not borrow and not current_user.is_admin:
        raise HTTPException(403, "You must have an approved borrow to view this book")
    
    # If file_path is a data URL (base64), decode and serve it
    if book.file_path.startswith('data:'):
        import base64
        import io
        
        # Extract base64 data after the comma
        try:
            base64_data = book.file_path.split(',')[1]
            pdf_bytes = base64.b64decode(base64_data)
            
            return StreamingResponse(
                io.BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"inline; filename={book.title}.pdf",
                    "Content-Security-Policy": "default-src 'self'"
                }
            )
        except Exception as e:
            raise HTTPException(400, f"Invalid PDF data: {str(e)}")
    
    # If it's a file path, stream it
    if not os.path.exists(book.file_path):
        raise HTTPException(404, "PDF file not found on server")
    
    def iterfile():
        with open(book.file_path, mode="rb") as file:
            yield from file
    
    return StreamingResponse(
        iterfile(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename={book.title}.pdf",
            "Content-Security-Policy": "default-src 'self'"
        }
    )

# @router.get("/{book_id}/read")
# def read_online(book_id: int, db: Session = Depends(get_db)):
#     book = db.query(Book).filter(Book.id == book_id).first()
#     return FileResponse(book.file_path)

# @router.get("/{book_id}/download")
# def download_book(book_id: int, db: Session = Depends(get_db)):
#     book = db.query(Book).filter(Book.id == book_id).first()
#     return FileResponse(book.file_path, filename=f"{book.title}.pdf")

@router.get("/categories")
def categories(db: Session = Depends(get_db)):
    raw = db.query(Book.category).distinct().all()
    return [c[0] for c in raw]
