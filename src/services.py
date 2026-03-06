"""
Utility services for the Civic Lens application.
Includes helper functions for common tasks.
"""

from datetime import datetime
from typing import Dict, Any


def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO format string"""
    return dt.isoformat()


def get_ai_confidence_level(confidence: float) -> str:
    """Convert confidence score to human-readable level"""
    if confidence >= 0.9:
        return "Very High"
    elif confidence >= 0.75:
        return "High"
    elif confidence >= 0.6:
        return "Medium"
    else:
        return "Low"


def create_audit_log(
    complaint_id: str, action: str, details: Dict[str, Any]
) -> Dict[str, Any]:
    """Create an audit log entry for complaint actions"""
    return {
        "complaint_id": complaint_id,
        "action": action,
        "timestamp": format_timestamp(datetime.utcnow()),
        "details": details,
    }


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Validate GPS coordinates are within valid ranges"""
    if -90 <= latitude <= 90 and -180 <= longitude <= 180:
        return True
    return False
