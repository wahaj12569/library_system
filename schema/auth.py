from pydantic import BaseModel,EmailStr

class LoginRequest(BaseModel):
    username: str
    password: str

# Token response
class Token(BaseModel):
    access_token: str
    token_type: str

class SignupRequest(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    password: str 

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

class AdminCreateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str