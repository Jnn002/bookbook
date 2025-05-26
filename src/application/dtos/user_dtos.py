from pydantic import BaseModel, EmailStr


class UserLoginDTO(BaseModel):
    email: EmailStr
    password: str


class PasswordResetDTO(BaseModel):
    new_password: str
    confirm_password: str
