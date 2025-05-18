from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Time
from sqlalchemy.orm import relationship
from src.models.base import Base

class Match(Base):
    __tablename__ = "matches"

    # Required fields
    match_id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.tournament_id"), nullable=False)
    
    # Nullable fields
    match_no = Column(String, nullable=True)
    activity_area_id = Column(Integer, nullable=True)
    activity_area_latitude = Column(Float, nullable=True)
    activity_area_longitude = Column(Float, nullable=True)
    activity_area_name = Column(String, nullable=True)
    activity_area_no = Column(String, nullable=True)
    adm_org_id = Column(Integer, nullable=True)
    arr_org_id = Column(Integer, nullable=True)
    arr_org_no = Column(String, nullable=True)
    arr_org_name = Column(String, nullable=True)
    awayteam_id = Column(Integer, nullable=True)
    awayteam_org_no = Column(String, nullable=True)
    awayteam = Column(String, nullable=True)
    awayteam_org_name = Column(String, nullable=True)
    awayteam_overridden_name = Column(String, nullable=True)
    awayteam_club_org_id = Column(Integer, nullable=True)
    hometeam_id = Column(Integer, nullable=True)
    hometeam = Column(String, nullable=True)
    hometeam_org_name = Column(String, nullable=True)
    hometeam_overridden_name = Column(String, nullable=True)
    hometeam_org_no = Column(String, nullable=True)
    hometeam_club_org_id = Column(Integer, nullable=True)
    round_id = Column(Integer, nullable=True)
    round_name = Column(String, nullable=True)
    season_id = Column(Integer, nullable=True)
    tournament_name = Column(String, nullable=True)
    match_date = Column(DateTime, nullable=True)
    match_start_time = Column(Integer, nullable=True)  # Stored as minutes since midnight (e.g. 1500 = 15:00)
    match_end_time = Column(Integer, nullable=True)
    venue_unit_id = Column(Integer, nullable=True)
    venue_unit_no = Column(String, nullable=True)
    venue_id = Column(Integer, nullable=True)
    venue_no = Column(String, nullable=True)
    physical_area_id = Column(Integer, nullable=True)
    home_goals = Column(Integer, nullable=True)
    away_goals = Column(Integer, nullable=True)
    match_end_result = Column(String, nullable=True)
    live_arena = Column(Boolean, nullable=True)
    live_client_type = Column(String, nullable=True)
    status_type_id = Column(Integer, nullable=True)
    status_type = Column(String, nullable=True)
    last_change_date = Column(DateTime, nullable=True)
    spectators = Column(Integer, nullable=True)
    actual_match_date = Column(DateTime, nullable=True)
    actual_match_start_time = Column(Integer, nullable=True)
    actual_match_end_time = Column(Integer, nullable=True)
    sport_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    # Relationships
    tournament = relationship("Tournament", back_populates="matches")