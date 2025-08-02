import httpx
import asyncio
import base64
from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from src.config.settings import Settings
from src.models.team_member_custom_data import TeamMemberCustomData
from src.utils.logging_config import setup_logging
from src.services.minio_service import MinioService
from datetime import timedelta
from typing import Dict, Optional

# Set up logging
logger = setup_logging("person_image_service")

class PersonImageService:
    def __init__(self):
        self.minio_service = MinioService()
    
    async def save_person_images(self, db: Session, person_id: int, image_url: Optional[str], image2_url: Optional[str]) -> None:
        """Download and save person images to MinIO"""

        existing_image = db.query(TeamMemberCustomData).filter(TeamMemberCustomData.person_id == person_id).first()

        image_object_key = None
        image2_object_key = None
        
        # Download and store primary image
        if image_url:
            image_object_key = await self.minio_service.download_and_store_image(person_id, image_url, True)
        
        # Download and store secondary image
        if image2_url:
            image2_object_key = await self.minio_service.download_and_store_image(person_id, image2_url, False)
        
        # Update database - much simpler now!
        if existing_image:
            if image_object_key:
                existing_image.image_object_key = image_object_key
                existing_image.original_image_url = image_url
            
            if image2_object_key:
                existing_image.image2_object_key = image2_object_key
                existing_image.original_image2_url = image2_url
            
            existing_image.updated_at = datetime.now()
            existing_image.last_fetched_at = datetime.now()
        else:
            new_image = TeamMemberCustomData(
                person_id=person_id,
                image_object_key=image_object_key,
                image2_object_key=image2_object_key,
                original_image_url=image_url,
                original_image2_url=image2_url,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                last_fetched_at=datetime.now()
            )
            db.add(new_image)
        
        try:
            db.commit()
            logger.info("Successfully saved person image references", extra={
                "person_id": person_id,
                "has_primary_image": image_object_key is not None,
                "has_secondary_image": image2_object_key is not None
            })
        except Exception as e:
            db.rollback()
            logger.error("Error saving person image references", extra={
                "person_id": person_id,
                "error": str(e)
            })
            raise

# get the urls for the images of a person
def get_person_image_urls(self, person_id: int, expires: timedelta = timedelta(hours=1)) -> Dict[str, Optional[str]]:
    """
    Get presigned URLs for a person's images by looking up the database first.
    This is more reliable than guessing the object key format.
    """
    from src.utils.database import get_db
    
    db = next(get_db())
    try:
        person_image = db.query(TeamMemberCustomData).filter(
            TeamMemberCustomData.person_id == person_id
        ).first()
        
        if not person_image:
            return {"primary_image_url": None, "secondary_image_url": None}
        
        primary_url = None
        secondary_url = None
        
        # Get primary image URL
        if person_image.image_object_key:
            try:
                primary_url = self.minio_service.get_image_url(person_image.image_object_key, expires)
            except Exception as e:
                logger.error(f"Error generating primary image URL for person {person_id}: {e}")
        
        # Get secondary image URL
        if person_image.image2_object_key:
            try:
                secondary_url = self.minio_service.get_image_url(person_image.image2_object_key, expires)
            except Exception as e:
                logger.error(f"Error generating secondary image URL for person {person_id}: {e}")
        
        return {
            "primary_image_url": primary_url,
            "secondary_image_url": secondary_url
        }
    finally:
        db.close()

def get_person_primary_image_url(self, person_id: int, expires: timedelta = timedelta(hours=1)) -> Optional[str]:
    """Get just the primary image URL for a person"""
    urls = self.get_person_image_urls(person_id, expires)
    return urls["primary_image_url"]