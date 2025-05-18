import httpx
from datetime import datetime
from sqlalchemy.orm import Session
from src.config.settings import Settings
from src.models.team import Team

class TeamService:
    def __init__(self):
        self.settings = Settings()
        self.base_url = self.settings.API_BASE_URL

    async def fetch_tournament_teams(self, tournament_id: int) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/ta/TournamentTeams/?tournamentId={tournament_id}"
            )
            response.raise_for_status()
            return response.json()

    def save_tournament_teams(self, db: Session, data: dict):
        tournament_id = data["tournamentId"]
        
        # First, delete existing teams for this tournament to avoid duplicates
        db.query(Team).filter(Team.tournament_id == tournament_id).delete()
        
        # Rollback needed after delete to ensure a clean session
        db.commit()
        
        try:
            for team_data in data.get("teams", []):
                team = Team(
                    team_id=team_data["teamId"],
                    tournament_id=tournament_id,
                    club_org_id=team_data["clubOrgId"],
                    team_no=team_data["teamNo"],
                    team_name=team_data["team"],
                    overridden_name=team_data["overriddenName"],
                    describing_name=team_data["describingName"]
                )
                db.add(team)
            
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error saving teams for tournament {tournament_id}: {e}")
            raise