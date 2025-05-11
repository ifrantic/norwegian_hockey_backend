from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.settings import get_settings
from src.models.tournament import Base

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
Base.metadata.create_all(bind=engine)  # Create tables
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()