import os
import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# 1. DATABASE CONNECTION
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./coach.db")

# Render uses 'postgres://', but SQLAlchemy requires 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FIXED: Modern way to avoid the MovedIn20Warning
Base = declarative_base()

# 2. DATABASE MODEL
class CoachCenter(Base):
    __tablename__ = "coaching_centers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    location = Column(String)
    rating = Column(Float)
    contact = Column(String)

# Automatically create tables in PostgreSQL
Base.metadata.create_all(bind=engine)

# 3. APP SETUP
app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. ROUTES
@app.get("/")
def read_root(request: Request, db: Session = Depends(get_db)):
    centers = db.query(CoachCenter).all()
    
    # Seed data if database is empty
    if not centers:
        sample_data = [
            CoachCenter(name="Speed Maths Academy", location="Dwaraka Nagar", rating=4.5, contact="9876543210"),
            CoachCenter(name="Vizag Tech Hub", location="MVP Colony", rating=4.8, contact="9988776655")
        ]
        db.add_all(sample_data)
        db.commit()
        centers = db.query(CoachCenter).all()

    return templates.TemplateResponse("index.html", {"request": request, "centers": centers})

# 5. THE FIX FOR RENDER DEPLOYMENT
if __name__ == "__main__":
    # Get the port from Render's environment, or use 10000 as default
    port = int(os.environ.get("PORT", 10000))
    
    # IMPORTANT: host must be "0.0.0.0" for Render to see the app
    uvicorn.run(app, host="0.0.0.0", port=port)
