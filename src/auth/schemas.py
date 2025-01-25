import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from src.books.schemas import Book
from src.errors import InvalidEmailStructure
from src.reviews.schemas import ReviewModel


class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=15)
    last_name: str = Field(max_length=15)
    username: str = Field(max_length=15)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)

    @field_validator('email')
    def validate_email(cls, v):
        from email_validator import EmailNotValidError, validate_email

        try:
            validate_email(v, check_deliverability=False)
            return v
        except EmailNotValidError:
            raise InvalidEmailStructure()


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
    reviews: list[ReviewModel]


class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)

    @field_validator('email')
    def validate_email(cls, v):
        from email_validator import EmailNotValidError, validate_email

        try:
            validate_email(v, check_deliverability=False)
            return v
        except EmailNotValidError:
            raise InvalidEmailStructure()


class EmailModel(BaseModel):
    addresses: list[str]


class PasswordResetRequestModel(BaseModel):
    email: str

    @field_validator('email')
    def validate_email(cls, v):
        from email_validator import EmailNotValidError, validate_email

        try:
            validate_email(v, check_deliverability=False)
            return v
        except EmailNotValidError:
            raise InvalidEmailStructure()


class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str
