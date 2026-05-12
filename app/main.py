from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
import math

# Import local project modules
from . import models, schemas, utils, database
from .database import engine, get_db

# This ensures the attendance.db file is ready
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="JKUAT GPS Attendance System")

# --- 1. CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. GEOFENCING SETTINGS ---
TARGET_LAT = -1.097519645519113  # JKUAT New Science Complex 
TARGET_LON = 37.01368667395922
ALLOWED_RADIUS_METERS = 500 

def get_distance(lat1, lon1, lat2, lon2):
    R = 6371000 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# --- 3. STUDENT REGISTRATION & LOGIN ---

@app.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = models.User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        student_registration_number=user.student_registration_number,
        hashed_password=utils.hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # DEBUG: See what is coming from the frontend in your terminal
    print(f"Login attempt for email: {form_data.username}")
    
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # Check if user exists and password is correct
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        print("Login failed: User not found or password incorrect")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )

    access_token = utils.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- 4. ATTENDANCE LOGGING ---

@app.post("/mark-attendance")
def mark_attendance(
    data: schemas.AttendanceCreate, 
    db: Session = Depends(get_db),
    current_user_email: str = Depends(utils.get_current_user)
):
    user = db.query(models.User).filter(models.User.email == current_user_email).first()
    distance = get_distance(data.latitude, data.longitude, TARGET_LAT, TARGET_LON)
    
    if distance <= ALLOWED_RADIUS_METERS:
        new_record = models.Attendance(
            student_id=user.id,
            course_code=data.course_code,
            latitude=data.latitude,
            longitude=data.longitude,
            status="Present",
            timestamp=datetime.utcnow()
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"message": f"Success! You are {round(distance, 1)}m away."}
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"Out of range! You are {round(distance/1000, 2)}km away."
        )

# --- 5. ANALYTICS ---

@app.get("/attendance-report")
def get_report(db: Session = Depends(get_db)):
    return db.query(models.Attendance).all()