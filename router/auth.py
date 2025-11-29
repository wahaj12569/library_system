from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from database.database import SessionLocal
from models.user import User
from utils.token import create_token

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# SIGNUP
# -----------------------------
class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == data.email).first()
    if exists:
        raise HTTPException(400, "Email already exists")

    user = User(
        username=data.username,
        email=data.email,
        password=pwd.hash(data.password)
    )
    db.add(user)
    db.commit()
    return {"message": "User created"}

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
# LOGOUT
# -----------------------------
@router.post("/logout")
def logout():
    return {"message": "Token invalidation is handled on client-side"}

# -----------------------------
# CREATE ADMIN
# -----------------------------
@router.post("/create-admin")
def create_admin(data: SignupRequest, db: Session = Depends(get_db)):
    user = User(
        username=data.username,
        email=data.email,
        password=pwd.hash(data.password),
        is_admin=True
    )
    db.add(user)
    db.commit()
    return {"message": "Admin created"}
