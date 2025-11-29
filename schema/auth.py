from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

# Token response
class Token(BaseModel):
    access_token: str
    token_type: str