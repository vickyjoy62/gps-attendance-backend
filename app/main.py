from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from . import models, schemas, database, utils

# 1. Initialize Database Tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="JKUAT GPS Attendance System")

# 2. JKUAT Geofence Configuration (Juja Campus Sample Hall)
TARGET_LAT = -1.0912
TARGET_LON = 37.0117
ALLOWED_RADIUS_METERS = 50.0 

# 3. Database Session Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def health_check():
    return {"status": "online", "message": "JKUAT Attendance Backend is Running"}

# --- PHASE 3: AUTHENTICATION ---

@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = utils.hash_password(user.password)
    
    new_user = models.User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        student_registration_number=user.student_registration_number,
        hashed_password=hashed_pwd
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = utils.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- PHASE 4: GPS GEOFENCING ---

@app.post("/mark-attendance")
def mark_attendance(attendance_data: schemas.AttendanceCreate):
    """
    Verifies student location using the Haversine formula.
    Fulfills the 'Prevent Proxy Sign-in' requirement.
    """
    # Calculate distance between student and classroom
    distance = utils.calculate_distance(
        attendance_data.latitude, 
        attendance_data.longitude, 
        TARGET_LAT, 
        TARGET_LON
    )
    
    # Check if student is within the 50m radius
    if distance > ALLOWED_RADIUS_METERS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=f"Access Denied: You are {round(distance, 2)}m away from the classroom."
        )
    
    # Success response (Phase 5 will link this to the database)
    return {
        "status": "success",
        "message": "You are within range. Attendance verified!",
        "distance_meters": round(distance, 2)
    }