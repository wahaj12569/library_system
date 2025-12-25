from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from database.database import Base, engine
from models.user import User
from models.books import Book
from models.borrow import Borrow
from router.auth import router as auth_router
from router.books import router as books_router
from router.borrow import router as borrow_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

# Temporary lightweight migrations to align DB schema with models
def _apply_simple_migrations():
    # Uses PostgreSQL IF NOT EXISTS to avoid errors on repeated runs
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE books ADD COLUMN IF NOT EXISTS picture_url TEXT"))
        conn.execute(text("ALTER TABLE books ADD COLUMN IF NOT EXISTS total_copies INTEGER DEFAULT 1"))
        conn.execute(text("ALTER TABLE books ADD COLUMN IF NOT EXISTS available_copies INTEGER DEFAULT 1"))

_apply_simple_migrations()

app.include_router(auth_router)
app.include_router(books_router)
app.include_router(borrow_router)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("frontend/index.html")
