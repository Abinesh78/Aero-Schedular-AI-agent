from sqlalchemy import Column, String, JSON, Float, DateTime
from datetime import datetime
from app.db import Base

class RosterVersion(Base):
    __tablename__ = "roster_versions"

    version_id = Column(String, primary_key=True)
    week_start = Column(String)
    correlation_id = Column(String)
    diff_json = Column(JSON)
    churn_rate = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, default="system")