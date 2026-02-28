from sqlalchemy import Column, String
from app.db import Base

class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(String, primary_key=True)
    day = Column(String)
    start = Column(String)
    end = Column(String)