from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from database.database import SessionLocal , get_db
from schema.auth import SignupRequest , UserResponse,AdminCreateRequest
from models.user import User
from utils.token import create_token
from config import Settings

router = APIRouter(prefix="/auth", tags=["Auth"])


pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = Settings().SECRET_KEY 
ALGORITHM = Settings().ALGORITHM


def hash_password(password: str):
    return pwd.hash(password)
# -----------------------------
# SIGNUp
# -----------------------------


@router.post("/signup")
async def signup(data: SignupRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        raise HTTPException(400, "Email already exists")
    hashed_password = hash_password(data.password)
    user = User(
        username=data.username,
        full_name=data.full_name,
        email=data.email,
        password=hashed_password
    )
    db.add(user)
    db.commit()
    return UserResponse(id=user.id, username=user.username, email=user.email)

# -----------------------------
# LOGIN
# -----------------------------
@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not pwd.verify(form.password, user.password):
        raise HTTPException(401, "Invalid credentials")

    token = create_token({"sub": user.username, "id": user.id})
    return {"access_token": token, "token_type": "bearer"}

# -----------------------------
# CURRENT USER
# -----------------------------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = data.get("sub")
        user = db.query(User).filter(User.username == username).first()
        return user
    except:
        raise HTTPException(401, "Invalid or expired token")

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "email": user.email}
# -----------------------------
# CREATE ADMIN
# -----------------------------
@router.post("/create-admin")
def create_admin(data: AdminCreateRequest, db: Session = Depends(get_db)):
    user = User(
        username=data.username,
        email=data.email,
        password=pwd.hash(data.password),
        is_admin=True
    )
    db.add(user)
    db.commit()
    return {"message": "Admin created"}
