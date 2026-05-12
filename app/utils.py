import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

# 1. SECURITY CONFIGURATIONS
# In a real JKUAT production environment, you'd put these in an .env file
SECRET_KEY = "JKUAT_GPS_ATTENDANCE_SECRET_KEY_2026" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 2. PASSWORD HASHING SETUP
# This tells Passlib to use the 'bcrypt' algorithm for security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 3. OAUTH2 SCHEME
# This tells FastAPI where to look for the token (the /login endpoint)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 4. HELPER FUNCTIONS

def verify_password(plain_password, hashed_password):
    """Checks if the typed password matches the one in the database."""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    """Converts a plain password into a secure hash before saving."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Generates the JWT 'Digital ID' for the student."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt