from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from src.models.tournament import Tournament
from src.models.base import Base

class Team(Base):
    __tablename__ = "teams"

    # Required fields
    team_id = Column(Integer, nullable=False)
    tournament_id = Column(Integer, ForeignKey("tournaments.tournament_id"), nullable=False)
    
    # Nullable fields
    club_org_id = Column(Integer, ForeignKey("organisations.org_id"), nullable=True)
    team_no = Column(Integer, nullable=True)
    team_name = Column(String, nullable=True)
    overridden_name = Column(String, nullable=True)
    describing_name = Column(String, nullable=True)

    tournament = relationship("Tournament", back_populates="teams")
    organisation = relationship("Organisation", back_populates="teams")

    # Define composite primary key and unique constraint
    __table_args__ = (
        PrimaryKeyConstraint('team_id', 'tournament_id'),
        {},
    )