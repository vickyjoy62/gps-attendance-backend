import math
import jwt
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jkuat_mobile_computing_secret_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24-hour token validity

# --- AUTHENTICATION UTILS ---

def hash_password(password: str):
    """
    Encrypts a plain text password.
    Truncates to 72 chars to prevent bcrypt ValueError.
    """
    return pwd_context.hash(password[:72])

def verify_password(plain_password, hashed_password):
    """Checks if entered password matches stored hash."""
    return pwd_context.verify(plain_password[:72], hashed_password)

def create_access_token(data: dict):
    """Generates a secure JWT token for the student session."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- GPS & GEOFENCING UTILS ---

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Haversine Formula: Calculates the distance in meters between two GPS points.
    Critical for verifying student presence within the JKUAT geofence.
    """
    # Earth's radius in kilometers
    R = 6371.0 

    # Convert coordinates from degrees to radians
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    # Apply the Haversine formula
    a = math.sin(dphi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Calculate distance in meters
    distance_meters = R * c * 1000
    return distance_meters