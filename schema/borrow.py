from datetime import datetime
from pydantic import BaseModel, validator


class BorrowRequest(BaseModel):
    book_id: int
    requested_borrow_date: datetime
    requested_return_date: datetime

    @validator('requested_return_date')
    def validate_return_date(cls, v, values):
        if 'requested_borrow_date' in values:
            borrow_date = values['requested_borrow_date']
            if v <= borrow_date:
                raise ValueError('Return date must be after borrow date')
            days_diff = (v - borrow_date).days
            if days_diff > 15:
                raise ValueError('Borrow period cannot exceed 15 days')
        return v


class BorrowReturnRequest(BaseModel):
    book_id: int


class BorrowApprovalRequest(BaseModel):
    borrow_id: int
    approve: bool


class BorrowBookInfo(BaseModel):
    id: int
    title: str
    author: str

    class Config:
        orm_mode = True


class BorrowUserInfo(BaseModel):
    id: int
    username: str
    email: str | None = None

    class Config:
        orm_mode = True


class BorrowResponse(BaseModel):
    id: int
    book: BorrowBookInfo
    user: BorrowUserInfo | None = None
    request_date: datetime
    requested_borrow_date: datetime | None = None
    requested_return_date: datetime | None = None
    borrow_date: datetime | None = None
    return_date: datetime | None = None
    status: str
    is_returned: bool

    class Config:
        orm_mode = True
