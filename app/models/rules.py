from sqlalchemy import Column, String, Text
from app.db import Base

class RulesDoc(Base):
    __tablename__ = "rules_docs"

    id = Column(String, primary_key=True)
    doc_name = Column(String)
    content = Column(Text)