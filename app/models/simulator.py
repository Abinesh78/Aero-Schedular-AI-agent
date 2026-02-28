from sqlalchemy import Column, String, Integer, JSON
from app.db import Base

class Simulator(Base):
    __tablename__ = "simulators"

    id = Column(String, primary_key=True)
    type = Column(String)
    availability = Column(JSON)
    max_sessions_per_day = Column(Integer)