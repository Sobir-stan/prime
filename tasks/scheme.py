from pydantic import BaseModel, Field

data = {
    "username": "al",
    "password" : "1234567",
    "email": None,
    "age" : 100
}

class userSchema(BaseModel):
    username : str = Field(min_length=3, max_length=50)
    password : str
    email : str | None
    age : int = Field(ge = 0, le=100)


userSchema(**data)

