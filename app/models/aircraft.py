from sqlalchemy import Column, String, JSON
from app.db import Base

class Aircraft(Base):
    __tablename__ = "aircraft"

    id = Column(String, primary_key=True)
    type = Column(String)
    maintenance = Column(JSON)
    availability = Column(JSON)