from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from app.database.db import Base

class PredictionRecord(Base):
    __tablename__ = "prediction_records"

    id = Column(Integer, primary_key=True, index=True)

    final_score = Column(Float)
    risk_level = Column(String)

    microbiome_score = Column(Float)
    voice_score = Column(Float)
    hrv_score = Column(Float)
    inflammation_score = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)