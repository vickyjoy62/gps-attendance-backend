from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    student_registration_number = Column(String, unique=True, index=True, nullable=False)
    # This MUST be exactly 'hashed_password'
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)