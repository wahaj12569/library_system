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
    print(f"Signup attempt for email: {data.email}, username: {data.username}")
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        print("Signup failed: email already exists")
        raise HTTPException(400, "Email already exists")
    hashed_password = hash_password(data.password)
    print(f"Password hashed: {hashed_password}")
    user = User(
        username=data.username,
        full_name=data.full_name,
        email=data.email,
        password=hashed_password
    )
    db.add(user)
    db.commit()
    print(f"User {data.username} created successfully")
    return UserResponse(id=user.id, username=user.username, email=user.email)

# -----------------------------
# LOGIN
# -----------------------------
@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print(f"Login attempt for username: {form.username}")
    user = db.query(User).filter(User.username == form.username).first()
    print(f"User found: {user is not None}")
    if user:
        print(f"Stored password hash: {user.password}")
        print(f"Password verify: {pwd.verify(form.password, user.password)}")
    if not user or not pwd.verify(form.password, user.password):
        print("Login failed: invalid credentials")
        raise HTTPException(401, "Invalid credentials")

    token = create_token({"sub": user.username, "id": user.id})
    print(f"Login successful for {form.username}")
    return {"access_token": token, "token_type": "bearer", "is_admin": user.is_admin, "username": user.username}

# -----------------------------
# CURRENT USER
# -----------------------------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = data.get("sub")
        print(f"Decoded username: {username}")
        user = db.query(User).filter(User.username == username).first()
        print(f"User found: {user}")
        if not user:
            raise HTTPException(401, "User not found")
        return user
    except Exception as e:
        print(f"Token decode error: {e}")
        raise HTTPException(401, "Invalid or expired token")

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "email": user.email, "full_name": user.full_name}

@router.put("/me")
def update_me(data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.full_name = data.get('full_name', user.full_name)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username, "email": user.email, "full_name": user.full_name}

@router.get("/users")
def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin can list users")
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "is_admin": u.is_admin,
        }
        for u in users
    ]

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin can delete users")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}
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
