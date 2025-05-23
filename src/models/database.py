from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.settings import get_settings
from src.models.base import Base
# import all models to ensure they are registered with SQLAlchemy
from src.models.tournament import Tournament, TournamentClass
from src.models.team import Team
from src.models.match import Match
from src.models.standing import Standing
from src.models.organisation import Organisation
from src.models.team_member import TeamMember


settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
Base.metadata.create_all(bind=engine) # Create all tables in the database which are defined by Base's subclasses
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()