from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional

# --- 1. USER SCHEMAS ---

# This is what the frontend sends during registration
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    student_registration_number: str

# This is the "Safe" version of a User we send back to React
# Notice: No password field here for security!
class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    student_registration_number: str
    is_active: bool

    class Config:
        from_attributes = True


# --- 2. AUTHENTICATION SCHEMAS ---

# This is what the backend sends back after a successful login
class Token(BaseModel):
    access_token: str
    token_type: str

# This represents the data inside the JWT token
class TokenData(BaseModel):
    email: Optional[str] = None


# --- 3. ATTENDANCE SCHEMAS (For the next step) ---

class AttendanceCreate(BaseModel):
    latitude: float
    longitude: float
    course_code: str

class AttendanceOut(BaseModel):
    id: int
    student_id: UUID
    course_code: str
    timestamp: str
    status: str

    class Config:
        from_attributes = True