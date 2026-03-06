from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class CategoryEnum(str, Enum):
    ROAD = "Road"
    MUNICIPAL = "Municipal"
    ELECTRICITY = "Electricity"
    WATER = "Water"


class StatusEnum(str, Enum):
    REGISTERED = "Registered"
    FORWARDED = "Forwarded"
    CLOSED = "Closed"


class ConsistencyEnum(str, Enum):
    CONSISTENT = "CONSISTENT"
    PARTIALLY_CONSISTENT = "PARTIALLY_CONSISTENT"
    INCONSISTENT = "INCONSISTENT"


class LocationSchema(BaseModel):
    latitude: float
    longitude: float


class ComplaintSubmissionRequest(BaseModel):
    description_user: Optional[str] = Field(
        None, description="Optional user-provided description"
    )
    category_user: Optional[str] = Field(None, description="User-selected category")
    location: LocationSchema = Field(..., description="GPS coordinates of the issue")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


class ImageAnalysisResponse(BaseModel):
    detected_objects: list[str]
    issue_type: str
    damage_level: Optional[str] = None
    visual_features: Dict[str, Any]
    confidence: float


class DescriptionGenerationResponse(BaseModel):
    generated_description: str
    keywords: list[str]
    detected_issue_type: str


class ConsistencyCheckResponse(BaseModel):
    status: ConsistencyEnum
    similarity_score: float
    explanation: str


class AutoCategoryResponse(BaseModel):
    category: CategoryEnum
    confidence: float
    reasoning: str


class DepartmentMapResponse(BaseModel):
    department: str
    category: CategoryEnum


class ComplaintRegistrationResponse(BaseModel):
    complaint_id: str
    status: StatusEnum
    image_url: str
    description_generated: Optional[str]
    category_ai: str
    ai_confidence: float
    consistency_status: Optional[ConsistencyEnum]
    consistency_score: Optional[float]
    department: str
    location: LocationSchema
    timestamp: datetime


class ComplaintDetailResponse(BaseModel):
    complaint_id: str
    image_url: str
    description_user: Optional[str]
    description_generated: Optional[str]
    category_user: Optional[str]
    category_ai: str
    consistency_score: Optional[float]
    consistency_status: Optional[str]
    location: Dict[str, float]
    department: str
    status: str
    timestamp: datetime
    ai_confidence: float
    image_analysis_results: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True
