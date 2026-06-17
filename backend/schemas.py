#Pydantic 数据校验
from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from datetime import datetime


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=32)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", v):
            raise ValueError("用户名必须以字母开头，仅允许字母、数字和下划线")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("密码必须包含至少一个字母")
        if not re.search(r"[0-9]", v):
            raise ValueError("密码必须包含至少一个数字")
        return v


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class RegisterResponseData(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime


class LoginResponseData(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserInfo


class ApiResponse(BaseModel):
    code: int
    message: str
    data: dict | None = None