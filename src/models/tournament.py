from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base


class Tournament(Base):
    __tablename__ = "tournaments"

    # Required fields
    tournament_id = Column(Integer, primary_key=True)
    season_id = Column(Integer, nullable=False)
    
    # Nullable fields
    tournament_no = Column(String, nullable=True)
    from_date = Column(DateTime, nullable=True)
    to_date = Column(DateTime, nullable=True)
    is_archival = Column(Boolean, nullable=True)
    is_deleted = Column(Boolean, nullable=True)
    org_id_owner = Column(Integer, nullable=True)
    parent_tournament_id = Column(Integer, nullable=True)
    season_name = Column(String, nullable=True)
    tournament_name = Column(String, nullable=True)
    tournament_short_name = Column(String, nullable=True)
    division = Column(Integer, nullable=True)
    logo_url = Column(String, nullable=True)
    is_table_published = Column(Boolean, nullable=True)
    is_result_published = Column(Boolean, nullable=True)
    are_matches_published = Column(Boolean, nullable=True)
    publish_matches_to_date = Column(DateTime, nullable=True)
    are_referees_published = Column(Boolean, nullable=True)
    publish_referees_to_date = Column(DateTime, nullable=True)
    are_statistics_published = Column(Boolean, nullable=True)
    are_teams_published = Column(Boolean, nullable=True)
    live_arena = Column(Boolean, nullable=True)
    live_client = Column(Boolean, nullable=True)
    withdrawals_visible = Column(Boolean, nullable=True)
    team_entry = Column(Boolean, nullable=True)
    tournament_type = Column(String, nullable=True)
    sport_id = Column(Integer, nullable=True)

    tournament_classes = relationship("TournamentClass", back_populates="tournament")
    matches = relationship("Match", back_populates="tournament")
    teams = relationship("Team", back_populates="tournament")
    standings = relationship("Standing", back_populates="tournament")
    player_statistics = relationship("PlayerStatistic", back_populates="tournament")
    
class TournamentClass(Base):
    __tablename__ = "tournament_classes"

    # Required fields
    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.tournament_id"), nullable=False)
    class_id = Column(Integer, nullable=False)
    
    # Nullable fields
    class_name = Column(String, nullable=True)
    from_age = Column(Integer, nullable=True)
    to_age = Column(Integer, nullable=True)
    allowed_from_age = Column(Integer, nullable=True)
    allowed_to_age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    live_arena_storage = Column(String, nullable=True)

    tournament = relationship("Tournament", back_populates="tournament_classes")
