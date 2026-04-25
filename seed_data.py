from app.database import SessionLocal, engine
from app import models
from geoalchemy2.elements import WKTElement
import uuid

db = SessionLocal()

def seed():
    # 1. Create a Test Student
    test_user = models.User(
        id=uuid.uuid4(),
        email="test_student@jkuat.ac.ke",
        first_name="Victoria",
        last_name="Joy",
        student_registration_number="JKUAT/001",
        password_hash="hashed_password_placeholder" # We'll do real hashing in Phase 3
    )
    
    # 2. Create a Test Class at JKUAT
    # Coordinates for JKUAT Assembly Hall: 1.1015° S, 37.0144° E
    # Point format: 'POINT(Longitude Latitude)'
    jkuat_coords = "POINT(37.0144 -1.1015)"
    
    test_class = models.ClassSession(
        id=uuid.uuid4(),
        course_code="BIT 2204",
        course_name="Mobile Computing",
        classroom_location=WKTElement(jkuat_coords, srid=4326),
        geofence_radius_meters=50
    )

    db.add(test_user)
    db.add(test_class)
    db.commit()
    print("✅ Successfully seeded JKUAT test data!")

if __name__ == "__main__":
    seed()