from sqlalchemy import Column, String, Boolean, Integer, JSON
from app.db import Base

class Instructor(Base):
    __tablename__ = "instructors"

    id = Column(String, primary_key=True)
    ratings = Column(JSON)
    currency_valid_until = Column(String)
    max_duty_hours_per_day = Column(Integer)
    sim_instructor = Column(Boolean)
    availability = Column(JSON)