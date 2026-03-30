import os
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import uvicorn

# 1. Database Configuration (The "Big Rock" Connection)
# On Render, it uses DATABASE_URL. Locally, it falls back to SQLite.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./coach.db")

# Fix for Render/PostgreSQL strings starting with 'postgres://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Updated to avoid the "MovedIn20Warning"
Base = declarative_base()

# 2. Database Model
class CoachCenter(Base):
    __tablename__ = "coaching_centers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    location = Column(String)
    rating = Column(Float)
    contact = Column(String)

# Create tables in the "Big Rock" (PostgreSQL)
Base.metadata.create_all(bind=engine)

# 3. FastAPI App Setup
app = FastAPI()

# Mount static files (CSS/JS) if you have a 'static' folder
# app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. Routes
@app.get("/")
def read_root(request: Request, db: Session = Depends(get_db)):
    centers = db.query(CoachCenter).all()
    
    # If database is empty (first run), add sample data
    if not centers:
        sample_data = [
            CoachCenter(name="Speed Maths Academy", location="Dwaraka Nagar", rating=4.5, contact="9876543210"),
            CoachCenter(name="Vizag Tech Hub", location="MVP Colony", rating=4.8, contact="9988776655"),
            CoachCenter(name="Govt Job Prep", location="Gajuwaka", rating=4.2, contact="9123456789"),
            CoachCenter(name="Python Masters", location="Siripuram", rating=4.9, contact="8877665544")
        ]
        db.add_all(sample_data)
        db.commit()
        centers = db.query(CoachCenter).all()

    return templates.TemplateResponse("index.html", {"request": request, "centers": centers})

# 5. The "Render-Ready" Start Logic
if __name__ == "__main__":
    # Render provides a PORT environment variable. Default to 10000 for local testing.
    port = int(os.environ.get("PORT", 10000))
    
    print(f"Starting CoachFinder Server on http://0.0.0.0:{port}")
    
    # host="0.0.0.0" allows the BigRock domain to connect to the server
    uvicorn.run(app, host="0.0.0.0", port=port)
