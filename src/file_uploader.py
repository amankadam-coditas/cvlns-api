import cloudinary
import cloudinary.uploader
from src.config import settings
from fastapi import UploadFile


class DocumentService:

    def __init__(self):
        pass

    def upload_document(self, image: UploadFile):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )
        print("check 02", id(settings))
        upload_result = cloudinary.uploader.upload(image.file)

        return upload_result.get("secure_url")
