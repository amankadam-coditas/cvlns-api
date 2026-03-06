from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Enum, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum

Base = declarative_base()


class CategoryEnum(str, PyEnum):
    ROAD = "Road"
    MUNICIPAL = "Municipal"
    ELECTRICITY = "Electricity"
    WATER = "Water"


class StatusEnum(str, PyEnum):
    REGISTERED = "Registered"
    FORWARDED = "Forwarded"
    CLOSED = "Closed"


class ConsistencyEnum(str, PyEnum):
    CONSISTENT = "CONSISTENT"
    PARTIALLY_CONSISTENT = "PARTIALLY_CONSISTENT"
    INCONSISTENT = "INCONSISTENT"


class Complaint(Base):
    __tablename__ = "complaints"

    complaint_id = Column(String, primary_key=True, index=True)
    image_url = Column(String, nullable=False)
    description_user = Column(String, nullable=True)
    description_generated = Column(String, nullable=True)
    category_user = Column(String(50), nullable=True)
    category_ai = Column(String(50), nullable=False)
    consistency_score = Column(Float, nullable=True)
    consistency_status = Column(String(50), default=ConsistencyEnum.CONSISTENT)
    location = Column(JSON, nullable=False)  # {latitude, longitude}
    department = Column(String(100), nullable=False)
    status = Column(String(50), default=StatusEnum.REGISTERED)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ai_confidence = Column(Float, nullable=False)
    image_analysis_results = Column(JSON, nullable=True)  # Store detailed AI analysis
