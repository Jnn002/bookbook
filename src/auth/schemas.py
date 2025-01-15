import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.books.schemas import Book


class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=15)
    last_name: str = Field(max_length=15)
    username: str = Field(max_length=15)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime


class UserBooksModel(UserModel):
    books: list[Book]


class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)
