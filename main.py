import os
import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Float, or_
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# 1. DATABASE CONFIGURATION
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./coach.db")

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
    category = Column(String)  # Added Category (e.g., UPSC, Coding, JEE)
    rating = Column(Float)
    contact = Column(String)

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

# 4. THE HOME ROUTE (With Search Support)
@app.get("/")
def read_root(request: Request, search: str = None, db: Session = Depends(get_db)):
    # 4a. Check if DB is empty and add 50 institutes
    if db.query(CoachCenter).count() == 0:
        institutes = []
        # Categories: IIT-JEE, NEET, UPSC, SSC, Coding, Spoken English, Music
        data = [
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
        
        # We loop to create 50 entries based on these examples
        for i in range(1, 51):
            base_info = data[i % len(data)]
            institutes.append(CoachCenter(
                name=f"{base_info[0]} Unit {i}",
                location=base_info[1],
                category=base_info[2],
                rating=base_info[3],
                contact=base_info[4]
            ))
        
        db.add_all(institutes)
        db.commit()

    # 4b. Handle Search Logic
    query = db.query(CoachCenter)
    if search:
        # Searches in name, location, or category
        query = query.filter(
            or_(
                CoachCenter.name.contains(search),
                CoachCenter.location.contains(search),
                CoachCenter.category.contains(search)
            )
        )
    
    centers = query.all()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"centers": centers, "search_query": search}
    )

# 5. RENDER LOGIC
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
