from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from src.models.base import Base
from datetime import datetime

class Organisation(Base):
    __tablename__ = "organisations"

    # Primary key
    org_id = Column(Integer, primary_key=True)
    
    # Basic info
    reference_id = Column(String, nullable=True)
    org_name = Column(String, nullable=True)
    abbreviation = Column(String, nullable=True)
    describing_name = Column(String, nullable=True)
    org_type_id = Column(Integer, nullable=True)
    organisation_number = Column(String, nullable=True)
    
    # Contact info
    email = Column(String, nullable=True)
    home_page = Column(String, nullable=True)
    mobile_phone = Column(String, nullable=True)
    
    # Address
    address_line1 = Column(String, nullable=True)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    country_id = Column(String, nullable=True)
    post_code = Column(String, nullable=True)
    
    # Coordinates
    longitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    
    # Media
    org_logo_base64 = Column(String, nullable=True)
    
    # Stats
    members = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)
    
    # Define relationships to teams - this will be a one-to-many relationship
    teams = relationship("Team", back_populates="organisation", foreign_keys="Team.club_org_id")