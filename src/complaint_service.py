import uuid
from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from src.models import Complaint, CategoryEnum, StatusEnum, ConsistencyEnum
from src.schemas import (
    ComplaintSubmissionRequest,
    ComplaintRegistrationResponse,
    LocationSchema,
)
from src.ai_service import AIService
from src.file_uploader import DocumentService


class ComplaintService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
        self.file_service = DocumentService()

    @staticmethod
    def generate_complaint_id() -> str:
        """Generate unique complaint ID"""
        return f"COMPLAINT-{uuid.uuid4().hex[:12].upper()}"

    @staticmethod
    def map_category_to_department(category: str) -> str:
        """Map category to respective department"""
        department_map = {
            "Road": "Public Works Department (PWD)",
            "Municipal": "Municipal Corporation",
            "Electricity": "Electricity Board",
            "Water": "Water Supply Department",
        }
        return department_map.get(category, "Municipal Corporation")

    async def process_complaint(
        self,
        image_url: str,
        submission_request: ComplaintSubmissionRequest,
        user_description: Optional[str] = None,
    ) -> ComplaintRegistrationResponse:
        """
        Complete workflow for processing a complaint:
        1. Analyze image
        2. Validate image quality
        3. Generate description if missing
        4. Check image-text consistency (if description provided)
        5. Auto-categorize
        6. Map to department
        7. Store in database
        """

        # Step 1: Analyze image
        image_analysis = self.ai_service.analyze_image(image_url)

        # Step 2: Validate image quality
        is_valid, quality_message = self.ai_service.validate_image_quality(
            image_analysis
        )
        if not is_valid:
            raise ValueError(f"Image validation failed: {quality_message}")

        # Step 3: Generate description if missing
        description_generated = None
        user_description_final = user_description
        if not user_description:
            desc_response = self.ai_service.generate_description(
                image_url, image_analysis
            )
            description_generated = desc_response.generated_description
            user_description_final = None
        else:
            desc_response = self.ai_service.generate_description(
                image_url, image_analysis
            )
            description_generated = desc_response.generated_description

        # Step 4: Check image-text consistency
        consistency_status = ConsistencyEnum.CONSISTENT
        consistency_score = 1.0
        if user_description:
            consistency_response = self.ai_service.validate_image_text_consistency(
                image_url, user_description, image_analysis
            )
            consistency_status = consistency_response.status
            consistency_score = consistency_response.similarity_score

        # Step 5: Auto-categorize
        category_response = self.ai_service.auto_categorize(
            image_analysis.issue_type,
            image_analysis.detected_objects,
            user_description,
        )

        # Step 6: Map to department
        department = self.map_category_to_department(category_response.category)

        # Step 7: Store in database
        complaint_id = self.generate_complaint_id()
        complaint = Complaint(
            complaint_id=complaint_id,
            image_url=image_url,
            description_user=user_description,
            description_generated=description_generated,
            category_user=submission_request.category_user,
            category_ai=category_response.category,
            consistency_score=consistency_score,
            consistency_status=consistency_status,
            location={
                "latitude": submission_request.location.latitude,
                "longitude": submission_request.location.longitude,
            },
            department=department,
            status=StatusEnum.REGISTERED,
            ai_confidence=category_response.confidence,
            image_analysis_results=image_analysis.model_dump(),
        )

        self.db.add(complaint)
        self.db.commit()
        self.db.refresh(complaint)

        return ComplaintRegistrationResponse(
            complaint_id=complaint_id,
            status=StatusEnum.REGISTERED,
            image_url=image_url,
            description_generated=description_generated,
            category_ai=str(category_response.category.value),
            ai_confidence=category_response.confidence,
            consistency_status=consistency_status,
            consistency_score=consistency_score,
            department=department,
            location=submission_request.location,
            timestamp=datetime.utcnow(),
        )

    def get_complaint(self, complaint_id: str):
        """Retrieve complaint details"""
        return (
            self.db.query(Complaint)
            .filter(Complaint.complaint_id == complaint_id)
            .first()
        )

    def list_complaints(self, limit: int = 50, offset: int = 0):
        """List all complaints with pagination"""
        return self.db.query(Complaint).offset(offset).limit(limit).all()

    def list_complaints_by_department(
        self, department: str, limit: int = 50, offset: int = 0
    ):
        """List complaints for specific department"""
        return (
            self.db.query(Complaint)
            .filter(Complaint.department == department)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def update_complaint_status(self, complaint_id: str, status: str):
        """Update complaint status"""
        complaint = self.get_complaint(complaint_id)
        if complaint:
            complaint.status = status
            self.db.commit()
            self.db.refresh(complaint)
        return complaint
