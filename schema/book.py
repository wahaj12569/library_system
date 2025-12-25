from pydantic import BaseModel

class BookCreate(BaseModel):
    title: str
    author: str
    description: str | None = None
    category: str | None = None
    picture_url: str | None = None
    file_path: str | None = None
    available_copies: int = 0
    total_copies: int = 0

class BookResponse(BaseModel):
    id: int
    title: str   
    author: str
    description: str | None = None
    category: str | None = None
    picture_url: str | None = None
    file_path: str | None = None
    total_copies: int
    available_copies: int

    class Config:
        orm_mode = True