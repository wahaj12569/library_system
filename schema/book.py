from pydantic import BaseModel

class BookCreate(BaseModel):
    title: str
    author: str
    description: str | None = None
    category: str | None = None
    file_path: str | None = None 
    available_copies: int = 0
    total_copies: int = 0

class BookResponse(BaseModel):
    id: int
    title: str   
    author: str