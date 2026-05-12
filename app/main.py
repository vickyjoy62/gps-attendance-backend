from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

# Import your local files
from . import models, schemas, utils, database
from .database import engine, get_db

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="JKUAT GPS Attendance System")

# --- 1. CORS CONFIGURATION ---
# This allows your React app (localhost:3000) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. AUTHENTICATION / LOGIN ---
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm uses 'username' for the email field
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create the JWT access token
    access_token_expires = timedelta(minutes=utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# --- 3. USER REGISTRATION ---
@app.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if registration number is unique
    db_reg = db.query(models.User).filter(
        models.User.student_registration_number == user.student_registration_number
    ).first()
    if db_reg:
        raise HTTPException(status_code=400, detail="Registration number already in use")

    # Hash the password and save
    hashed_password = utils.hash_password(user.password)
    new_user = models.User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        student_registration_number=user.student_registration_number,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- 4. ATTENDANCE (PLACEHOLDER) ---
@app.post("/mark-attendance")
def mark_attendance(token: str = Depends(utils.oauth2_scheme), db: Session = Depends(get_db)):
    # This is where we will verify GPS coordinates in the next step
    return {"message": "Endpoint reached successfully"}

@app.get("/")
def read_root():
    return {"message": "JKUAT GPS Attendance API is running"}