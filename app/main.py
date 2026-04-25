from fastapi import FastAPI
from app.database import engine
from app import models

# 1. This magical line tells SQLAlchemy to look at your models.py 
# and create the corresponding tables in your Docker database!
models.Base.metadata.create_all(bind=engine)

# 2. Initialize the FastAPI application
app = FastAPI(
    title="GPS Attendance API",
    description="Backend for verifying student attendance via GPS coordinates.",
    version="1.0.0"
)

# 3. Create a simple test endpoint
@app.get("/")
def health_check():
    return {
        "status": "success",
        "message": "The GPS Attendance API is running perfectly!"
    }