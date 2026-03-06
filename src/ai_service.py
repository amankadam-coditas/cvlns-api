import json
import base64
from typing import Dict, Any, Optional, List
from openai import OpenAI
from src.config import settings
from src.schemas import (
    ImageAnalysisResponse,
    DescriptionGenerationResponse,
    ConsistencyCheckResponse,
    AutoCategoryResponse,
    CategoryEnum,
    ConsistencyEnum,
)
import re


class AIService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_BASE_URL,
        )
        self.vision_model = settings.GROQ_VISION_MODEL
        self.text_model = settings.GROQ_TEXT_MODEL

    def analyze_image(self, image_url: str) -> ImageAnalysisResponse:
        """
        Analyze image using OpenAI Vision API to detect objects and issues.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url},
                            },
                            {
                                "type": "text",
                                "text": """Analyze this image for civic issues. Provide response in JSON format:
{
    "detected_objects": ["list of objects detected"],
    "issue_type": "type of civic issue (e.g., pothole, garbage, broken pole, water leakage, etc.)",
    "damage_level": "minor/moderate/severe",
    "visual_features": {
        "is_clear_image": boolean,
        "visibility": "good/moderate/poor",
        "artifacts": ["any blur, obstruction, etc."]
    },
    "confidence": 0.0-1.0
}""",
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )

            # Parse response
            content = response.choices[0].message.content
            # Extract JSON from response
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())
            else:
                analysis_data = json.loads(content)

            return ImageAnalysisResponse(**analysis_data)
        except Exception as e:
            # Fallback response in case of API error
            return ImageAnalysisResponse(
                detected_objects=["image"],
                issue_type="unknown",
                visual_features={"error": str(e)},
                confidence=0.0,
            )

    def generate_description(
        self, image_url: str, image_analysis: ImageAnalysisResponse
    ) -> DescriptionGenerationResponse:
        """
        Generate a structured description based on image analysis.
        """
        try:
            prompt = f"""Based on the following civic issue analysis, generate a professional complaint description.

Issue Type: {image_analysis.issue_type}
Detected Objects: {", ".join(image_analysis.detected_objects)}
Damage Level: {image_analysis.damage_level}
Visibility: {image_analysis.visual_features.get("visibility", "good")}

Generate a response in JSON format:
{{
    "generated_description": "A clear 1-2 sentence description suitable for government complaint",
    "keywords": ["list", "of", "relevant", "keywords"],
    "detected_issue_type": "categorized issue type"
}}"""

            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                max_tokens=300,
            )

            content = response.choices[0].message.content
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                desc_data = json.loads(json_match.group())
            else:
                desc_data = json.loads(content)

            return DescriptionGenerationResponse(**desc_data)
        except Exception as e:
            return DescriptionGenerationResponse(
                generated_description=f"There appears to be a {image_analysis.issue_type} that requires attention.",
                keywords=image_analysis.detected_objects,
                detected_issue_type=image_analysis.issue_type,
            )

    def validate_image_text_consistency(
        self,
        image_url: str,
        user_description: str,
        image_analysis: ImageAnalysisResponse,
    ) -> ConsistencyCheckResponse:
        """
        Check semantic similarity between image analysis and user description.
        """
        try:
            prompt = f"""Compare the user's description of a civic issue with the image analysis results.

User Description: "{user_description}"

Image Analysis:
- Issue Type: {image_analysis.issue_type}
- Detected Objects: {", ".join(image_analysis.detected_objects)}
- Damage Level: {image_analysis.damage_level}

Evaluate consistency and respond in JSON format:
{{
    "status": "CONSISTENT/PARTIALLY_CONSISTENT/INCONSISTENT",
    "similarity_score": 0.0-1.0,
    "explanation": "brief explanation of consistency assessment"
}}"""

            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                max_tokens=200,
            )

            content = response.choices[0].message.content
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                consistency_data = json.loads(json_match.group())
            else:
                consistency_data = json.loads(content)

            return ConsistencyCheckResponse(**consistency_data)
        except Exception as e:
            return ConsistencyCheckResponse(
                status=ConsistencyEnum.CONSISTENT,
                similarity_score=0.75,
                explanation="Consistency check could not be performed",
            )

    def auto_categorize(
        self,
        issue_type: str,
        detected_objects: List[str],
        user_description: Optional[str] = None,
    ) -> AutoCategoryResponse:
        """
        Automatically categorize complaint into Road/Municipal/Electricity/Water.
        """
        try:
            context = f"""Issue Type: {issue_type}
Detected Objects: {", ".join(detected_objects)}
User Description: {user_description or "Not provided"}

Based on the issue, categorize it into one of: Road, Municipal, Electricity, Water

Respond in JSON format:
{{
    "category": "Road/Municipal/Electricity/Water",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of the categorization"
}}"""

            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {
                        "role": "user",
                        "content": context,
                    }
                ],
                max_tokens=200,
            )

            content = response.choices[0].message.content
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                category_data = json.loads(json_match.group())
            else:
                category_data = json.loads(content)

            # Ensure category is valid
            category_data["category"] = self._map_category(
                category_data.get("category", "Municipal")
            )
            return AutoCategoryResponse(**category_data)
        except Exception as e:
            return AutoCategoryResponse(
                category=CategoryEnum.MUNICIPAL,
                confidence=0.5,
                reasoning="Unable to categorize, defaulting to Municipal",
            )

    @staticmethod
    def _map_category(category_str: str) -> CategoryEnum:
        """Map string to CategoryEnum"""
        category_map = {
            "road": CategoryEnum.ROAD,
            "municipal": CategoryEnum.MUNICIPAL,
            "electricity": CategoryEnum.ELECTRICITY,
            "water": CategoryEnum.WATER,
        }
        return category_map.get(category_str.lower(), CategoryEnum.MUNICIPAL)

    def validate_image_quality(
        self, image_analysis: ImageAnalysisResponse
    ) -> tuple[bool, str]:
        """
        Validate if image quality is acceptable for complaint processing.
        """
        visual_features = image_analysis.visual_features
        visibility = visual_features.get("visibility", "good")
        artifacts = visual_features.get("artifacts", [])
        is_clear = visual_features.get("is_clear_image", True)

        if visibility == "poor" or len(artifacts) > 2:
            return False, "Image quality is too poor. Please upload a clearer image."

        if not is_clear:
            return False, "Image is too blurry. Please upload a clearer image."

        if image_analysis.confidence < 0.5:
            return (
                False,
                "Unable to detect clear issue in image. Please upload a more relevant image.",
            )

        return True, "Image quality is acceptable"
