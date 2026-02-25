from pydantic import BaseModel, Field


class Body_test(BaseModel):
    username: str = Field(min_length=5, max_length=20)
    age: int = Field(gt=0, le=100)

class New_user(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=6)

class Login_user(BaseModel):
    username: str
    password: str