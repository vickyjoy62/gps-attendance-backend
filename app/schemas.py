from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    student_registration_number: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    device_id: Optional[str] = None

    class Config:
        from_attributes = True