from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

# This is the base class for our database models
Base = declarative_base()

class Institute(Base):
    __tablename__ = "institutes" # Name of the table in PostgreSQL
    
    id = Column(Integer, primary_key=True, index=True) # Unique ID for each center
    name = Column(String) # Name of the Coaching Center
    category = Column(String) # 'Government' or 'Software'
    course = Column(String) # e.g., 'UPSC', 'Python Full Stack'
    city = Column(String) # Location
    rating = Column(Float) # User rating (e.g., 4.5)
