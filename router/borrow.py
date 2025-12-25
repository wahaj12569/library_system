from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database.database import SessionLocal
from models.borrow import Borrow
from models.books import Book
from models.user import User
from router.auth import get_current_user
from schema.borrow import (
    BorrowRequest,
    BorrowReturnRequest,
    BorrowApprovalRequest,
    BorrowResponse,
    BorrowUserInfo,
)

router = APIRouter(prefix="/borrow", tags=["Borrow"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/request", response_model=BorrowResponse, status_code=201)
def request_borrow(
    data: BorrowRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """User requests to borrow a book with requested dates"""
    book = db.query(Book).filter(Book.id == data.book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")
    
    # Check if book has available copies
    if book.available_copies <= 0:
        raise HTTPException(400, "No copies available for this book")
    
    # Check for any existing request or borrow for this book by this user (not returned/rejected)
    existing = db.query(Borrow).filter(
        Borrow.user_id == user.id,
        Borrow.book_id == data.book_id,
        Borrow.status.in_(["pending", "approved"]),
        Borrow.is_returned == False
    ).first()
    
    if existing:
        if existing.status == "pending":
            raise HTTPException(400, "You already have a pending request for this book. Please wait for admin approval.")
        elif existing.status == "approved":
            raise HTTPException(400, "You have already borrowed this book. Please return it before requesting again.")
    
    # Check if user has any active approved borrow (not returned) for this same book
    active_borrow = db.query(Borrow).filter(
        Borrow.user_id == user.id,
        Borrow.book_id == data.book_id,
        Borrow.status == "approved",
        Borrow.is_returned == False
    ).first()
    
    if active_borrow:
        raise HTTPException(400, "You currently have this book borrowed. Please return it first.")

    borrow = Borrow(
        user_id=user.id,
        book_id=data.book_id,
        requested_borrow_date=data.requested_borrow_date,
        requested_return_date=data.requested_return_date,
        status="pending"
    )

    db.add(borrow)
    db.commit()
    db.refresh(borrow)
    return _serialize_borrow(borrow, user)

@router.post("/approve", response_model=BorrowResponse)
def approve_borrow(
    data: BorrowApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Admin approves or rejects a borrow request"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin can approve borrows")
    
    borrow = db.query(Borrow).filter(Borrow.id == data.borrow_id).first()
    if not borrow:
        raise HTTPException(404, "Borrow request not found")
    
    if borrow.status != "pending":
        raise HTTPException(400, f"Request is already {borrow.status}")
    
    if data.approve:
        book = db.query(Book).filter(Book.id == borrow.book_id).first()
        if book.available_copies <= 0:
            raise HTTPException(400, "No copies available")
        
        borrow.status = "approved"
        borrow.borrow_date = datetime.utcnow()
        book.available_copies -= 1
    else:
        borrow.status = "rejected"
    
    db.commit()
    db.refresh(borrow)
    return _serialize_borrow(borrow, None)

@router.post("/return", response_model=BorrowResponse)
def return_book(
    data: BorrowReturnRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    borrow = (
        db.query(Borrow)
        .filter(
            Borrow.book_id == data.book_id,
            Borrow.user_id == user.id,
            Borrow.status == "approved",
            Borrow.is_returned == False,
        )
        .first()
    )

    if not borrow:
        raise HTTPException(400, "No approved borrow found for this book")

    borrow.is_returned = True
    borrow.status = "returned"
    borrow.return_date = datetime.utcnow()
    book = db.query(Book).filter(Book.id == data.book_id).first()
    book.available_copies += 1

    db.commit()
    db.refresh(borrow)
    return _serialize_borrow(borrow, user)

@router.get("/my", response_model=list[BorrowResponse])
def my_borrowed(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    borrows = db.query(Borrow).filter(Borrow.user_id == user.id).all()
    return [_serialize_borrow(b, user) for b in borrows]

@router.get("/pending", response_model=list[BorrowResponse])
def pending_requests(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Admin gets all pending borrow requests"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin can view pending requests")
    borrows = db.query(Borrow).filter(Borrow.status == "pending").all()
    return [_serialize_borrow(b, None) for b in borrows]

@router.get("/all", response_model=list[BorrowResponse])
def all_borrows(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin can view borrows")
    borrows = db.query(Borrow).all()
    return [_serialize_borrow(b, None) for b in borrows]

@router.post("/admin/return/{borrow_id}", response_model=BorrowResponse)
def admin_return(
    borrow_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin can mark returns")

    borrow = db.query(Borrow).filter(Borrow.id == borrow_id).first()
    if not borrow:
        raise HTTPException(404, "Borrow not found")
    if borrow.is_returned:
        return _serialize_borrow(borrow, None)

    borrow.is_returned = True
    borrow.status = "returned"
    borrow.return_date = datetime.utcnow()
    book = db.query(Book).filter(Book.id == borrow.book_id).first()
    if book:
        book.available_copies += 1
    db.commit()
    db.refresh(borrow)
    return _serialize_borrow(borrow, None)

@router.get("/status/{book_id}")
def borrow_status(book_id: int, db: Session = Depends(get_db)):
    count = db.query(Borrow).filter(Borrow.book_id == book_id, Borrow.is_returned == False).count()
    return {"borrowed_count": count}

@router.get("/availability/{book_id}")
def book_availability(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    return {"total": book.total_copies, "available": book.available_copies}


def _serialize_borrow(borrow: Borrow, user_override: User | None):
    # Use override when we already have the current user to avoid another lookup
    user_obj = user_override if user_override else None
    if not user_obj:
        user_obj = borrow.user if hasattr(borrow, "user") else None

    user_info = None
    if user_obj:
        user_info = BorrowUserInfo(
            id=user_obj.id,
            username=user_obj.username,
            email=user_obj.email,
        )

    # Convert Book object to BorrowBookInfo
    from schema.borrow import BorrowBookInfo
    book_info = BorrowBookInfo(
        id=borrow.book.id,
        title=borrow.book.title,
        author=borrow.book.author,
    )

    return BorrowResponse(
        id=borrow.id,
        book=book_info,
        user=user_info,
        request_date=borrow.request_date,
        requested_borrow_date=borrow.requested_borrow_date,
        requested_return_date=borrow.requested_return_date,
        borrow_date=borrow.borrow_date,
        return_date=borrow.return_date,
        status=borrow.status,
        is_returned=borrow.is_returned,
    )

