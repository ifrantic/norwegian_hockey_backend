from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from src.models.base import Base
from datetime import datetime

class TeamMember(Base):
    __tablename__ = "team_members"

    # Primary key (composite)
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False)
    
    # Personal info
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)
    gender = Column(String, nullable=True)
    height = Column(Float, nullable=True)
    
    # Player/team info
    number = Column(String, nullable=True)
    position = Column(String, nullable=True)
    owning_org_id = Column(Integer, nullable=True)
    member_type = Column(String, nullable=True)  # Player, Coach, etc.
    
    # Media
    image_url = Column(String, nullable=True)
    image2_url = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)
    
    # Relationships
    team = relationship("Team", back_populates="members")
    
    # Unique constraint to avoid duplicates
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )