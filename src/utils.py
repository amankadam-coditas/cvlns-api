"""
Utility functions for the Civic Lens application.
"""

import re
import json
from typing import Optional, Dict, Any


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON object from text that may contain extra narrative.
    Useful for parsing AI model responses.
    """
    try:
        # Try to find JSON object in the text
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return None
    except (json.JSONDecodeError, ValueError):
        return None


def sanitize_string(input_str: str, max_length: int = 1000) -> str:
    """
    Sanitize user input by removing special characters and limiting length.
    """
    if not input_str:
        return ""

    # Remove excessive whitespace
    sanitized = " ".join(input_str.split())

    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."

    return sanitized


def get_issue_severity(damage_level: str) -> int:
    """
    Convert damage level string to priority number.
    Lower number = higher priority
    """
    severity_map = {
        "critical": 0,
        "severe": 1,
        "high": 1,
        "moderate": 2,
        "medium": 2,
        "minor": 3,
        "low": 3,
    }
    return severity_map.get(damage_level.lower(), 3)


def truncate_description(description: str, max_length: int = 500) -> str:
    """Truncate description to maximum length"""
    if len(description) <= max_length:
        return description
    return description[:max_length].rsplit(" ", 1)[0] + "..."


def format_category_name(category: str) -> str:
    """Format category name for display"""
    return category.replace("_", " ").title()
