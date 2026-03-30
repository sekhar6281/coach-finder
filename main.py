import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- 1. DATABASE CONFIGURATION ---
# If on Render, it uses Postgres. If on your Laptop, it creates coach.db (SQLite).
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./coach.db")

# Fix for Render's 'postgres://' vs SQLAlchemy's 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 2. DATABASE MODEL ---
class Institute(Base):
    __tablename__ = "institutes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    category = Column(String) # 'Government' or 'Software'
    course = Column(String)
    city = Column(String)
    rating = Column(Float)

# --- 3. LIFESPAN (Startup Logic) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create tables automatically
    Base.metadata.create_all(bind=engine)
    
    # 2. Add sample data if the database is empty
    db = SessionLocal()
    if db.query(Institute).count() == 0:
        sample_centers = [
            Institute(name="Vikas IAS Academy", category="Government", course="UPSC", city="Delhi", rating=4.8),
            Institute(name="TechMaster Pro", category="Software", course="Python Full Stack", city="Hyderabad", rating=4.5),
            Institute(name="Banking Career Hub", category="Government", course="IBPS PO", city="Bangalore", rating=4.2),
            Institute(name="CodeCraft Institute", category="Software", course="Java & Spring Boot", city="Pune", rating=4.7)
        ]
        db.add_all(sample_centers)
        db.commit()
    db.close()
    yield

# --- 4. FASTAPI APP ---
app = FastAPI(title="CoachFinder API", lifespan=lifespan)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 5. API ROUTES ---

# This route serves your Frontend (index.html)
@app.get("/")
async def read_index():
    return FileResponse('index.html')

# This route handles the search logic
@app.get("/search")
def search(category: str = None, city: str = None, db: Session = Depends(get_db)):
    query = db.query(Institute)
    if category:
        query = query.filter(Institute.category.ilike(f"%{category}%"))
    if city:
        query = query.filter(Institute.city.ilike(f"%{city}%"))
    return query.all()

# --- 6. RUN THE SERVER ---
if __name__ == "__main__":
    print("Starting CoachFinder Server on http://127.0.0.1:8000")
    # Using the string "main:app" is the most stable way to run uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
