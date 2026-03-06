from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from src.database import get_db
from src.complaint_service import ComplaintService
from src.file_uploader import DocumentService
from src.schemas import (
    ComplaintSubmissionRequest,
    LocationSchema,
    ComplaintRegistrationResponse,
    ComplaintDetailResponse,
    CategoryEnum,
)
import json

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


@router.post("/submit", response_model=ComplaintRegistrationResponse)
async def submit_complaint(
    file: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Submit a civic complaint with image.

    Required:
    - file: Image file
    - latitude: GPS latitude
    - longitude: GPS longitude

    Optional:
    - description: User-provided description
    - category: User-selected category (Road/Municipal/Electricity/Water)
    """
    try:
        # Upload image to Cloudinary
        file_service = DocumentService()
        image_url = file_service.upload_document(file)

        # Create submission request
        submission_request = ComplaintSubmissionRequest(
            description_user=description,
            category_user=category,
            location=LocationSchema(latitude=latitude, longitude=longitude),
        )

        # Process complaint
        complaint_service = ComplaintService(db)
        result = await complaint_service.process_complaint(
            image_url, submission_request, description
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing complaint: {str(e)}"
        )


@router.get("/status/{complaint_id}", response_model=ComplaintDetailResponse)
def get_complaint_status(complaint_id: str, db: Session = Depends(get_db)):
    """Get complaint details by ID"""
    complaint_service = ComplaintService(db)
    complaint = complaint_service.get_complaint(complaint_id)

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    return ComplaintDetailResponse.model_validate(complaint)


@router.get("/list", response_model=list[ComplaintDetailResponse])
def list_complaints(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all complaints with pagination"""
    complaint_service = ComplaintService(db)
    complaints = complaint_service.list_complaints(limit=limit, offset=skip)

    return [ComplaintDetailResponse.model_validate(c) for c in complaints]


@router.get("/department/{department}", response_model=list[ComplaintDetailResponse])
def get_department_complaints(
    department: str, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
):
    """Get complaints for a specific department"""
    complaint_service = ComplaintService(db)
    complaints = complaint_service.list_complaints_by_department(
        department=department, limit=limit, offset=skip
    )

    if not complaints:
        raise HTTPException(
            status_code=404, detail="No complaints found for this department"
        )

    return [ComplaintDetailResponse.model_validate(c) for c in complaints]


@router.put("/status/{complaint_id}")
def update_complaint_status(
    complaint_id: str, status: str, db: Session = Depends(get_db)
):
    """Update complaint status (for department use)"""
    valid_statuses = ["Registered", "Forwarded", "Closed"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}"
        )

    complaint_service = ComplaintService(db)
    complaint = complaint_service.update_complaint_status(complaint_id, status)

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    return ComplaintDetailResponse.model_validate(complaint)


@router.get("/departments")
def get_departments():
    """Get list of all departments"""
    return {
        "departments": [
            "Public Works Department (PWD)",
            "Municipal Corporation",
            "Electricity Board",
            "Water Supply Department",
        ]
    }


@router.get("/categories")
def get_categories():
    """Get list of all complaint categories"""
    return {"categories": [cat.value for cat in CategoryEnum]}


@router.post("/validate-image")
async def validate_image_quality(
    file: UploadFile = File(...),
):
    """Validate image quality before submission"""
    try:
        from src.ai_service import AIService
        from src.file_uploader import DocumentService

        # Upload image temporarily
        file_service = DocumentService()
        image_url = file_service.upload_document(file)

        # Analyze image
        ai_service = AIService()
        image_analysis = ai_service.analyze_image(image_url)

        # Validate quality
        is_valid, message = ai_service.validate_image_quality(image_analysis)

        return {
            "is_valid": is_valid,
            "message": message,
            "analysis": image_analysis.model_dump() if is_valid else None,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating image: {str(e)}")
