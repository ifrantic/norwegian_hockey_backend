# src/models/player_statistic.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from src.models.base import Base
from datetime import datetime

class PlayerStatistic(Base):
    __tablename__ = "player_statistics"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    tournament_id = Column(Integer, ForeignKey("tournaments.tournament_id"), nullable=False)
    person_id = Column(Integer, nullable=False)
    org_id = Column(Integer, nullable=False)
    
    # Player info
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    team_name = Column(String(255), nullable=False)
    team_short_name = Column(String(50), nullable=True)
    position = Column(String(50), nullable=True)
    
    # Statistics
    rank = Column(Integer, nullable=True)
    scoring_points = Column(Integer, nullable=False, default=0)  # This was "pts" from API - Goals + Assists  
    games_played = Column(Integer, nullable=False, default=0)
    goals_scored = Column(Integer, nullable=False, default=0)
    assists = Column(Integer, nullable=False, default=0)
    plus_minus = Column(Integer, nullable=False, default=0)  # This was "points" from API - +/- rating
    pim = Column(Integer, nullable=False, default=0)  # Penalty minutes
    
    # Power play stats
    power_play_goals = Column(Integer, nullable=False, default=0)
    power_play_goal_assists = Column(Integer, nullable=False, default=0)
    
    # Short handed stats
    short_handed_goals = Column(Integer, nullable=False, default=0)
    short_handed_goal_assists = Column(Integer, nullable=False, default=0)
    
    # Other stats
    gwg = Column(Integer, nullable=False, default=0)  # Game winning goals
    shots = Column(Integer, nullable=False, default=0)
    shots_pct = Column(Float, nullable=True)  # Shooting percentage
    face_offs = Column(Integer, nullable=False, default=0)
    faceoffs_win_pct = Column(Float, nullable=True)  # Face-off win percentage
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure one record per player per tournament
    __table_args__ = (
        UniqueConstraint('tournament_id', 'person_id', name='uq_player_tournament_stats'),
    )
    
    # Relationships
    tournament = relationship("Tournament", back_populates="player_statistics")