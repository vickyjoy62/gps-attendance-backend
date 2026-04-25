from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from . import models, schemas, database, utils

# Initialize the database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="JKUAT GPS Attendance System")

# Dependency to get a database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def health_check():
    return {"status": "success", "message": "Security Layer is Active!"}

# --- PHASE 3: AUTHENTICATION ROUTES ---

@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password using our security utility
    hashed_pwd = utils.hash_password(user.password)
    
    # Create the user object
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
    # Look for the user (FastAPI uses 'username' field for the login email)
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # Verify existence and password match
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Generate the JWT Token (The 'Digital Key' for the mobile app)
    access_token = utils.create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}