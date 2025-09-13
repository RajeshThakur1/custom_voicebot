
from pydantic import BaseModel, EmailStr
from typing import Optional

# todo Operations
class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = 1
    complete: bool = False

class TodoCreate(TodoBase):
    pass

class TodoResponse(TodoBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

# user Operations
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: Optional[str] = "user"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True