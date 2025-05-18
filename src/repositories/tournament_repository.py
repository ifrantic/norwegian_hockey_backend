from sqlalchemy.orm import Session
from src.models.tournament import Tournament, TournamentClass

class TournamentRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, tournament_id: int) -> Tournament:
        return self.db.query(Tournament).filter(Tournament.tournament_id == tournament_id).first()
    
    def get_by_season(self, season_id: int) -> list[Tournament]:
        return self.db.query(Tournament).filter(Tournament.season_id == season_id).all()
    
    def save(self, tournament: Tournament) -> Tournament:
        self.db.merge(tournament)
        self.db.commit()
        return tournament
        
    def delete(self, tournament_id: int) -> bool:
        result = self.db.query(Tournament).filter(Tournament.tournament_id == tournament_id).delete()
        self.db.commit()
        return result > 0