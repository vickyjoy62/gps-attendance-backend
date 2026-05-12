from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from uuid import UUID

# --- USER SCHEMAS (Phase 3) ---

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    student_registration_number: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID  # Fixed: Use UUID to match the database type
    is_active: bool

    class Config:
        from_attributes = True


# --- AUTHENTICATION SCHEMAS ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None


# --- ATTENDANCE SCHEMAS (Phase 4 & 5) ---

class AttendanceCreate(BaseModel):
    """
    Data required from the mobile app to verify location.
    """
    latitude: float
    longitude: float

class AttendanceResponse(BaseModel):
    """
    Data returned after attendance is successfully marked.
    """
    id: UUID
    user_id: UUID
    latitude: float
    longitude: float
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True