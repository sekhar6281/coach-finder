import os
import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Float, or_
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# 1. DATABASE CONFIGURATION
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
    category = Column(String) 
    rating = Column(Float)
    contact = Column(String)

# Create tables in the database (PostgreSQL on Render or SQLite locally)
Base.metadata.create_all(bind=engine)

# 3. APP SETUP
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. THE HOME ROUTE (With Search & 50 Sample Institutes)
@app.get("/")
def read_root(request: Request, search: str = None, db: Session = Depends(get_db)):
    # 4a. Auto-populate 50 institutes if database is empty
    if db.query(CoachCenter).count() == 0:
        institutes = []
        # Sample data to rotate through
        data_samples = [
            ("Speed Maths Academy", "Dwaraka Nagar", "Competitive", 4.5, "9876543210"),
            ("Vizag Tech Hub", "MVP Colony", "Coding", 4.8, "9988776655"),
            ("Chaitanya IIT", "Gajuwaka", "IIT-JEE", 4.2, "9123456789"),
            ("Narayana Medical", "Asilmetta", "NEET", 4.3, "8877665544"),
            ("Civil Services Point", "Siripuram", "UPSC", 4.7, "7766554433"),
            ("English Edge", "Madhurawada", "Spoken English", 4.0, "6655443322"),
            ("Data Science Pro", "Daba Gardens", "Coding", 4.9, "5544332211"),
            ("Bankers Adda", "Akkayyapalem", "Banking", 4.1, "4433221100"),
            ("Victory Sports", "Beach Road", "Sports", 4.6, "3322110099"),
            ("Sangeeth Music School", "Seethammadhara", "Music", 4.4, "2211009988")
        ]
        
        # Generate 50 entries
        for i in range(1, 51):
            base = data_samples[i % len(data_samples)]
            institutes.append(CoachCenter(
                name=f"{base[0]} - Branch {i}",
                location=base[1],
                category=base[2],
                rating=base[3],
                contact=base[4]
            ))
        
        db.add_all(institutes)
        db.commit()

    # 4b. Handle Search Logic
    query = db.query(CoachCenter)
    if search:
        query = query.filter(
            or_(
                CoachCenter.name.contains(search),
                CoachCenter.location.contains(search),
                CoachCenter.category.contains(search)
            )
        )
    
    centers = query.all()

    # 4c. Render Template with Named Arguments (Fixes 500 error)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"centers": centers, "search_query": search}
    )

# 5. EXECUTION LOGIC (Optimized for Render & Local Ubuntu)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    # host="0.0.0.0" is required for Render deployment
    uvicorn.run(app, host="0.0.0.0", port=port)
