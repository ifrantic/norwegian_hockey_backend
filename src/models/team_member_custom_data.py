from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from src.models.base import Base
from datetime import datetime

class TeamMemberCustomData(Base):
    __tablename__ = "team_member_custom_data"

    # Primary key
    person_id = Column(Integer, primary_key=True)
    
    # # Image data
    # image_base64 = Column(Text, nullable=True)  # Base64 encoded image
    # image2_base64 = Column(Text, nullable=True)  # Second image if available
    
        # MinIO object keys (paths)
    image_object_key = Column(String, nullable=True)    # MinIO object key for primary image
    image2_object_key = Column(String, nullable=True)   # MinIO object key for secondary image
    
    
    # Original URLs for reference/debugging
    original_image_url = Column(String, nullable=True)
    original_image2_url = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)
    last_fetched_at = Column(DateTime, nullable=True)  # When image was last downloaded
    
    # Additional custom fields you might want later
    notes = Column(String, nullable=True)