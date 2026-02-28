from sqlalchemy import Column, String, JSON, DateTime
from datetime import datetime
from app.db import Base

class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id = Column(String, primary_key=True)
    input_hash = Column(String)
    diff_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)