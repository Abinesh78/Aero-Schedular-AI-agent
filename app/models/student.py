from sqlalchemy import Column, String, Boolean, Integer, JSON
from app.db import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True)
    availability = Column(JSON)
    stage = Column(String)
    priority = Column(Integer)
    solo_eligible = Column(Boolean)
    required_sorties_per_week = Column(Integer)