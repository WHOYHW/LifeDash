#Pydantic 数据校验
from pydantic import BaseModel, Field, field_validator
import re
from datetime import datetime, date
from typing import Union
from typing import Optional


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=8, max_length=32)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", v):
            raise ValueError("用户名必须以字母开头，仅允许字母、数字和下划线")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", v):
            raise ValueError("邮箱格式不正确")
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
    data: Optional[object] = None


class TodoCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[Union[datetime, date]] = None
    tag: Optional[str] = None

    @field_validator("due_date", mode="before")
    @classmethod
    def parse_due_date(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, (datetime, date)):
            return v
        if isinstance(v, str):
            v = v.strip()
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S",
                        "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M",
                        "%Y-%m-%d"):
                try:
                    return datetime.strptime(v, fmt)
                except ValueError:
                    continue
        return v


class TodoUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[Union[datetime, date]] = None
    tag: Optional[str] = None
    is_completed: Optional[bool] = None

    @field_validator("due_date", mode="before")
    @classmethod
    def parse_due_date(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, (datetime, date)):
            return v
        if isinstance(v, str):
            v = v.strip()
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S",
                        "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M",
                        "%Y-%m-%d"):
                try:
                    return datetime.strptime(v, fmt)
                except ValueError:
                    continue
        return v


class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    priority: str
    due_date: Optional[datetime] = None
    tag: Optional[str] = None
    is_completed: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S"),
        }