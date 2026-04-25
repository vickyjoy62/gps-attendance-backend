import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_registration_number = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    device_id = Column(String, nullable=True)

class ClassSession(Base):
    __tablename__ = "classes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_code = Column(String, index=True)
    course_name = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    # SRID 4326 is the standard coordinate system for GPS (WGS 84)
    classroom_location = Column(Geometry('POINT', srid=4326)) 
    geofence_radius_meters = Column(Integer, default=50)

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String) # E.g., 'Present', 'Late', 'Failed_Location'
    recorded_location = Column(Geometry('POINT', srid=4326))

class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"))
    generated_at = Column(DateTime, default=datetime.utcnow)
    total_enrolled = Column(Integer, default=0)
    total_present = Column(Integer, default=0)
    attendance_percentage = Column(Float, default=0.0)
    report_file_url = Column(String, nullable=True)