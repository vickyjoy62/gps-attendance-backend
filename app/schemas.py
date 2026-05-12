from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# --- USER SCHEMAS (Requirement 7 & 15) ---

class UserCreate(BaseModel):
    """Schema for creating a new student account."""
    email: EmailStr
    first_name: str
    last_name: str
    student_registration_number: str
    password: str

class UserOut(BaseModel):
    """Schema for returning student data (excludes password for security)."""
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    student_registration_number: str

    class Config:
        # Allows compatibility with SQLAlchemy models
        from_attributes = True

# --- ATTENDANCE SCHEMAS (Requirement 3 & 18) ---

class AttendanceCreate(BaseModel):
    """Schema for sending GPS coordinates from the phone/laptop."""
    course_code: str
    latitude: float
    longitude: float

class AttendanceOut(BaseModel):
    """Schema for the 'Immediate Reports' view."""
    id: int
    student_id: int
    course_code: str
    latitude: float
    longitude: float
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True

# --- TOKEN SCHEMAS (Security) ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None