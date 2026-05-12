from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

# --- STUDENT TABLE (Requirement 7 & 15) ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    student_registration_number = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Relationship to link attendance to this student
    attendances = relationship("Attendance", back_populates="student")

# --- ATTENDANCE LOGS TABLE (Requirement 1, 3 & 18) ---
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    course_code = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String, default="Present") # Marks if student was in range
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Link back to the User model
    student = relationship("User", back_populates="attendances")