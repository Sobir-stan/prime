from pydantic import BaseModel, Field
import app

data = {
    "username": "john_doe",
    "password": "securepassword123",
    "email": ""
}

class userSchema(BaseModel):
    username : str = Field(min_length=3, max_length=50)
    password : str
    email : str | None
    age : int = Field(ge = 0, le=100)


userSchema(**data)


