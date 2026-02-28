from sqlalchemy import Column, String, JSON
from app.db import Base

class Roster(Base):
    __tablename__ = "rosters"

    id = Column(String, primary_key=True)
    week_start = Column(String)
    base_icao = Column(String)
    roster_json = Column(JSON)