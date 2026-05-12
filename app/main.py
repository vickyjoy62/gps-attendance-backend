from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from . import models, schemas, database, utils
from typing import List
from uuid import UUID

# 1. Initialize Database Tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="JKUAT GPS Attendance System",
    description="Secure GPS-based attendance with JWT Authentication and Haversine Geofencing",
    version="1.0.0"
)

# 2. Security Configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 3. Geofence Configuration (Juja Campus Sample Hall)
TARGET_LAT = -1.0912
TARGET_LON = 37.0117
ALLOWED_RADIUS_METERS = 50.0 

# 4. Database Session Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper to get current user from token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email = utils.verify_token(token) # We'll ensure this is in your utils.py
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/")
def health_check():
    return {"status": "online", "message": "JKUAT Attendance Backend is Running"}

# --- PHASE 3: AUTHENTICATION ---

@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
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

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = utils.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- PHASE 4 & 5: SECURE GPS GEOFENCING ---

@app.post("/mark-attendance", response_model=schemas.AttendanceResponse)
def mark_attendance(
    attendance_data: schemas.AttendanceCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Calculate distance
    distance = utils.calculate_distance(
        attendance_data.latitude, 
        attendance_data.longitude, 
        TARGET_LAT, 
        TARGET_LON
    )
    
    # 2. Geofence Check
    if distance > ALLOWED_RADIUS_METERS:
        raise HTTPException(
            status_code=403, 
            detail=f"Access Denied: You are {round(distance, 2)}m away from the classroom."
        )
    
    # 3. Save Record tied to the logged-in student
    new_record = models.Attendance(
        user_id=current_user.id,
        latitude=attendance_data.latitude,
        longitude=attendance_data.longitude,
        status="Present"
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    
    # Add distance to response so user knows how accurate it was
    new_record.message = "Attendance marked successfully!"
    new_record.distance = round(distance, 2)
    
    return new_record

# --- PHASE 6: REPORTING ---

@app.get("/attendance-logs", response_model=List[schemas.AttendanceResponse])
def get_attendance_logs(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Only authenticated users can see logs."""
    return db.query(models.Attendance).all()