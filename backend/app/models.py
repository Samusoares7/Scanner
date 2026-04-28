from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class ScanResult(Base):
    __tablename__ = "scan_results"
    id = Column(Integer, primary_key=True, index=True)
    target = Column(String, nullable=False)
    total_open_ports = Column(Integer)
    results = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
