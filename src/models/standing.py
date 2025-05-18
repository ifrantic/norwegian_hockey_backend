# src/models/standing.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base
from datetime import datetime

class Standing(Base):
    __tablename__ = "standings"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.tournament_id"), nullable=False)
    team_id = Column(Integer, nullable=False)  # This is the orgId in the API response
    
    # Basic team info
    team_name = Column(String, nullable=True)
    overridden_name = Column(String, nullable=True)
    position = Column(Integer, nullable=True)
    entry_id = Column(Integer, nullable=True)
    
    # Match stats - totals
    matches_played = Column(Integer, nullable=True)
    matches_home = Column(Integer, nullable=True)
    matches_away = Column(Integer, nullable=True)
    
    # Points
    points = Column(Integer, nullable=True)
    points_home = Column(Integer, nullable=True)
    points_away = Column(Integer, nullable=True)
    points_start = Column(Integer, nullable=True)
    total_points = Column(Integer, nullable=True)
    
    # Victories
    victories = Column(Integer, nullable=True)
    victories_home = Column(Integer, nullable=True)
    victories_away = Column(Integer, nullable=True)
    victories_fulltime_total = Column(Integer, nullable=True)
    victories_fulltime_home = Column(Integer, nullable=True)
    victories_fulltime_away = Column(Integer, nullable=True)
    victories_overtime_total = Column(Integer, nullable=True)
    victories_overtime_home = Column(Integer, nullable=True)
    victories_overtime_away = Column(Integer, nullable=True)
    victories_penalties_total = Column(Integer, nullable=True)
    victories_penalties_home = Column(Integer, nullable=True)
    victories_penalties_away = Column(Integer, nullable=True)
    
    # Draws
    draws = Column(Integer, nullable=True)
    draws_home = Column(Integer, nullable=True)
    draws_away = Column(Integer, nullable=True)
    
    # Losses
    losses = Column(Integer, nullable=True)
    losses_home = Column(Integer, nullable=True)
    losses_away = Column(Integer, nullable=True)
    losses_fulltime_total = Column(Integer, nullable=True)
    losses_fulltime_home = Column(Integer, nullable=True)
    losses_fulltime_away = Column(Integer, nullable=True)
    losses_overtime_total = Column(Integer, nullable=True)
    losses_overtime_home = Column(Integer, nullable=True)
    losses_overtime_away = Column(Integer, nullable=True)
    losses_penalties_total = Column(Integer, nullable=True)
    losses_penalties_home = Column(Integer, nullable=True)
    losses_penalties_away = Column(Integer, nullable=True)
    
    # Goals
    goals_scored = Column(Integer, nullable=True)
    goals_scored_home = Column(Integer, nullable=True)
    goals_scored_away = Column(Integer, nullable=True)
    goals_conceded = Column(Integer, nullable=True)
    goals_conceded_home = Column(Integer, nullable=True)
    goals_conceded_away = Column(Integer, nullable=True)
    goals_diff = Column(Integer, nullable=True)
    goals_ratio = Column(Float, nullable=True)
    
    # Penalty minutes
    penalty_minutes = Column(Integer, nullable=True)
    
    # Record strings
    home_record = Column(String, nullable=True)
    away_record = Column(String, nullable=True)
    
    # Formatted strings
    goals_home_formatted = Column(String, nullable=True)
    goals_away_formatted = Column(String, nullable=True)
    total_goals_formatted = Column(String, nullable=True)
    
    # Additional fields
    team_penalty = Column(String, nullable=True)
    team_penalty_negative = Column(Integer, nullable=True)
    team_penalty_positive = Column(Integer, nullable=True)
    dispensation = Column(Boolean, nullable=True)
    team_entry_status = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="standings")
    
    # Unique constraint to ensure a team only appears once per tournament
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )