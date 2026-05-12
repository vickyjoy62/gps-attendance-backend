from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# --- USER SCHEMAS (Phase 3) ---

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    student_registration_number: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    is_active: bool

    class Config:
        from_attributes = True

# --- ATTENDANCE SCHEMAS (Phase 4 & 5) ---

class AttendanceCreate(BaseModel):
    """
    Schema for capturing GPS coordinates from the mobile device.
    Fulfills the 'Capture student's location' requirement.
    """
    latitude: float
    longitude: float

class AttendanceResponse(BaseModel):
    """
    Schema for returning the verification result to the student.
    """
    id: str
    status: str
    message: str
    distance: float
    timestamp: datetime

    class Config:
        from_attributes = True