import os
import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# 1. DATABASE CONFIGURATION
# Render provides the URL. Fallback to local SQLite for Ubuntu testing.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./coach.db")

# MANDATORY FIX: SQLAlchemy requires 'postgresql://' instead of 'postgres://'
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. DATABASE MODEL
class CoachCenter(Base):
    __tablename__ = "coaching_centers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    location = Column(String)
    rating = Column(Float)
    contact = Column(String)

# Create tables in the PostgreSQL "Big Rock"
Base.metadata.create_all(bind=engine)

# 3. APP SETUP
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. THE HOME ROUTE
@app.get("/")
def read_root(request: Request, db: Session = Depends(get_db)):
    # Fetch all coaching centers
    centers = db.query(CoachCenter).all()
    
    # If the database is empty, add sample data
    if not centers:
        sample_data = [
            CoachCenter(name="Speed Maths Academy", location="Dwaraka Nagar", rating=4.5, contact="9876543210"),
            CoachCenter(name="Vizag Tech Hub", location="MVP Colony", rating=4.8, contact="9988776655"),
            CoachCenter(name="Python Masters", location="Siripuram", rating=4.9, contact="8877665544")
        ]
        db.add_all(sample_data)
        db.commit()
        # Refresh the list after adding data
        centers = db.query(CoachCenter).all()

    # MODERN FIX: Passing context using named arguments to avoid TypeError
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"centers": centers}
    )

# 5. RENDER DEPLOYMENT LOGIC
if __name__ == "__main__":
    # Get the port from Render's environment
    port = int(os.environ.get("PORT", 10000))
    
    # host="0.0.0.0" allows external traffic to reach the app
    uvicorn.run(app, host="0.0.0.0", port=port)
