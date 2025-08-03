import asyncio
import httpx
from minio import Minio
from minio.error import S3Error
from datetime import datetime, timedelta
from typing import Optional, Tuple
from io import BytesIO
from src.config.settings import get_settings
from src.utils.logging_config import setup_logging

logger = setup_logging("minio_service")

class MinioService:
    def __init__(self):
        self.settings = get_settings()
        
        # Validate required secrets
        self._validate_configuration()

        # Initialize MinIO client
        self.client = Minio(
            self.settings.MINIO_ENDPOINT.replace('http://', '').replace('https://', ''),
            access_key=self.settings.MINIO_ACCESS_KEY,
            secret_key=self.settings.MINIO_SECRET_KEY,
            secure=self.settings.MINIO_SECURE
        )
        
        # Ensure bucket exists
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.settings.MINIO_BUCKET):
                self.client.make_bucket(self.settings.MINIO_BUCKET)
                logger.info(f"Created bucket: {self.settings.MINIO_BUCKET}")
            else:
                logger.info(f"Bucket exists: {self.settings.MINIO_BUCKET}")
        except S3Error as e:
            logger.error(f"Error checking/creating bucket: {e}")
            raise
    
    def _generate_object_key(self, person_id: int, is_primary: bool = True, image_format: str = "jpg") -> str:
        """Generate a consistent object key for person images"""
        suffix = "primary" if is_primary else "secondary"
        return f"persons/{person_id}_{suffix}.{image_format}"
    
    async def download_and_store_image(self, person_id: int, image_url: str, is_primary: bool = True) -> Optional[str]:
        """
        Download image from URL and store in MinIO.
        Returns the object key if successful, None otherwise.
        """
        if not image_url:
            return None
        
        try:
            # Download image
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image_data = response.content
            
            # Determine format from content-type
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                image_format = 'jpg'
            elif 'png' in content_type:
                image_format = 'png'
            elif 'gif' in content_type:
                image_format = 'gif'
            else:
                image_format = 'jpg'  # Default
            
            # Generate object key
            object_key = self._generate_object_key(person_id, is_primary, image_format)
            
            # Upload to MinIO
            self.client.put_object(
                bucket_name=self.settings.MINIO_BUCKET,
                object_name=object_key,
                data=BytesIO(image_data),
                length=len(image_data),
                content_type=f'image/{image_format}'
            )
            
            logger.info("Successfully uploaded image to MinIO", extra={
                "person_id": person_id,
                "object_key": object_key,
                "size_bytes": len(image_data),
                "format": image_format
            })
            
            return object_key
            
        except Exception as e:
            logger.error("Failed to download and store image", extra={
                "person_id": person_id,
                "image_url": image_url[:100] + "..." if len(image_url) > 100 else image_url,
                "error": str(e)
            })
            return None
    
    def get_image_url(self, object_key: str, expires: timedelta = timedelta(hours=1)) -> str:
        """Generate a presigned URL for accessing an image"""
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.settings.MINIO_BUCKET,
                object_name=object_key,
                expires=expires
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise
    
    def delete_image(self, object_key: str) -> bool:
        """Delete an image from MinIO"""
        try:
            self.client.remove_object(self.settings.MINIO_BUCKET, object_key)
            logger.info(f"Deleted image: {object_key}")
            return True
        except S3Error as e:
            logger.error(f"Error deleting image {object_key}: {e}")
            return False
    
    def image_exists(self, object_key: str) -> bool:
        """Check if an image exists in MinIO"""
        try:
            self.client.stat_object(self.settings.MINIO_BUCKET, object_key)
            return True
        except S3Error:
            return False
        
    def _validate_configuration(self):
        """Validate that all required MinIO configuration is present"""
        if not self.settings.MINIO_ACCESS_KEY or self.settings.MINIO_ACCESS_KEY:
            raise ValueError("MINIO_ACCESS_KEY not properly configured")
        
        if not self.settings.MINIO_SECRET_KEY or self.settings.MINIO_SECRET_KEY:
            raise ValueError("MINIO_SECRET_KEY not properly configured")
        
        if not self.settings.MINIO_ENDPOINT:
            raise ValueError("MINIO_ENDPOINT not configured")
        
        logger.info(f"MinIO configured for {self.settings.ENVIRONMENT} environment")