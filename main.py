from fastapi import FastAPI
from database.database import engine,Base
from models import user ,books  # Ensure models are imported to register them with SQLAlchemy



api=FastAPI()

Base.metadata.create_all(bind=engine)

@api.get("/")
def root():
    return {"message":"Library API Testing"}