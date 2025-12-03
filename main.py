from fastapi import FastAPI
from database.database import Base, engine
from models.user import User
from models.books import Book
from models.borrow import Borrow
from router.auth import router as auth_router
from router.books import router as books_router
from router.borrow import router as borrow_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(books_router)
app.include_router(borrow_router)

@app.get("/")
def home():
    return {"message": "Library API Ready!"}
