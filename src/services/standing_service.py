# src/services/standing_service.py
import httpx
from datetime import datetime
from sqlalchemy.orm import Session
import asyncio
from src.config.settings import Settings
from src.models.standing import Standing
from src.utils.logging_config import setup_logging

# Set up logging
logger = setup_logging("standing_service")

class StandingService:
    def __init__(self):
        self.settings = Settings()
        self.base_url = self.settings.API_BASE_URL

    async def fetch_tournament_standings(self, tournament_id: int, max_retries: int = 3) -> dict:
        """Fetch standings for a given tournament"""
        if not isinstance(tournament_id, int) or tournament_id <= 0:
            raise ValueError(f"Invalid tournament_id: {tournament_id}")
            
        retries = 0
        logger.info("Fetching tournament standings", extra={
            "tournament_id": tournament_id,
            "retry_count": retries,
            "max_retries": max_retries
        })
        
        while retries < max_retries:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        f"{self.base_url}/ta/TournamentStandings/?tournamentId={tournament_id}"
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # API might return an error message instead of standings
                    if isinstance(data, dict) and "errorMessage" in data:
                        logger.warning("API returned error message", extra={
                            "tournament_id": tournament_id,
                            "error_message": data["errorMessage"]
                        })
                        return {"tournamentId": tournament_id, "standings": []}
                    
                    # Handle case where API returns array or just a single standings object
                    if isinstance(data, list):
                        standings = data
                    elif isinstance(data, dict) and "standings" in data:
                        standings = data.get("standings", [])
                    else:
                        standings = [data] if data else []
                    
                    logger.info("Successfully fetched standings", extra={
                        "tournament_id": tournament_id,
                        "standings_count": len(standings)
                    })
                    
                    # Ensure we have a properly structured response
                    return {
                        "tournamentId": tournament_id,
                        "standings": standings
                    }
            
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                retries += 1
                logger.warning("API request failed, retrying", extra={
                    "tournament_id": tournament_id,
                    "retry_count": retries,
                    "max_retries": max_retries,
                    "error": str(e),
                    "wait_seconds": 2 ** retries
                })
                
                if retries == max_retries:
                    logger.error("Failed to fetch standings after maximum retries", extra={
                        "tournament_id": tournament_id,
                        "retry_count": retries,
                        "error": str(e)
                    })
                    raise Exception(f"Failed to fetch standings after {max_retries} attempts: {str(e)}")
                    
                await asyncio.sleep(2 ** retries)  # Exponential backoff

    def save_tournament_standings(self, db: Session, data: dict):
        """Save tournament standings to the database"""
        tournament_id = data["tournamentId"]
        
        # First, delete existing standings for this tournament to avoid duplicates
        db.query(Standing).filter(Standing.tournament_id == tournament_id).delete()
        
        # Commit the delete operation before adding new standings
        db.commit()
        
        standings_to_add = []
        for standing_data in data.get("standings", []):
            # The API response might vary, so we need to handle both formats
            # In some responses, orgId is used for team ID
            team_id = standing_data.get("teamId") or standing_data.get("orgId")
            if not team_id:
                logger.warning("Standing data missing teamId/orgId", extra={
                    "tournament_id": tournament_id,
                    "standing_data": standing_data
                })
                continue
                
            # Determine team name from available fields
            team_name = (standing_data.get("teamName") or 
                        standing_data.get("orgName") or 
                        "Unknown")
                
            standing = Standing(
                tournament_id=tournament_id,
                team_id=team_id,
                team_name=team_name,
                overridden_name=standing_data.get("overriddenName"),
                position=standing_data.get("position"),
                entry_id=standing_data.get("entryId"),
                
                # Match stats
                matches_played=standing_data.get("matches"),
                matches_home=standing_data.get("matchesHome"),
                matches_away=standing_data.get("matchesAway"),
                
                # Points
                points=standing_data.get("points") or standing_data.get("totalPoints"),
                points_home=standing_data.get("pointsHome"),
                points_away=standing_data.get("pointsAway"),
                points_start=standing_data.get("pointsStart"),
                total_points=standing_data.get("totalPoints"),
                
                # Victories
                victories=standing_data.get("victories"),
                victories_home=standing_data.get("victoriesHome"),
                victories_away=standing_data.get("victoriesAway"),
                victories_fulltime_total=standing_data.get("victoriesFulltimeTotal"),
                victories_fulltime_home=standing_data.get("victoriesFulltimeHome"),
                victories_fulltime_away=standing_data.get("victoriesFulltimeAway"),
                victories_overtime_total=standing_data.get("victoriesOvertimeTotal"),
                victories_overtime_home=standing_data.get("victoriesOvertimeHome"),
                victories_overtime_away=standing_data.get("victoriesOvertimeAway"),
                victories_penalties_total=standing_data.get("victoriesPenaltiesTotal"),
                victories_penalties_home=standing_data.get("victoriesPenaltiesHome"),
                victories_penalties_away=standing_data.get("victoriesPenaltiesAway"),
                
                # Draws
                draws=standing_data.get("draws"),
                draws_home=standing_data.get("drawsHome"),
                draws_away=standing_data.get("drawsAway"),
                
                # Losses
                losses=standing_data.get("losses"),
                losses_home=standing_data.get("lossesHome"),
                losses_away=standing_data.get("lossesAway"),
                losses_fulltime_total=standing_data.get("lossesFulltimeTotal"),
                losses_fulltime_home=standing_data.get("lossesFulltimeHome"),
                losses_fulltime_away=standing_data.get("lossesFulltimeAway"),
                losses_overtime_total=standing_data.get("lossesOvertimeTotal"),
                losses_overtime_home=standing_data.get("lossesOvertimeHome"),
                losses_overtime_away=standing_data.get("lossesOvertimeAway"),
                losses_penalties_total=standing_data.get("lossesPenaltiesTotal"),
                losses_penalties_home=standing_data.get("lossesPenaltiesHome"),
                losses_penalties_away=standing_data.get("lossesPenaltiesAway"),
                
                # Goals
                goals_scored=standing_data.get("goalsScored") or standing_data.get("totalGoals"),
                goals_scored_home=standing_data.get("goalsScoredHome"),
                goals_scored_away=standing_data.get("goalsScoredAway"),
                goals_conceded=standing_data.get("goalsConceeded"),
                goals_conceded_home=standing_data.get("goalsConcededHome"),
                goals_conceded_away=standing_data.get("goalsConcededAway"),
                goals_diff=standing_data.get("goalDifference") or standing_data.get("goalsDiff"),
                goals_ratio=standing_data.get("goalRatio"),
                
                # Penalty minutes
                penalty_minutes=standing_data.get("penaltyMinutes"),
                
                # Record strings
                home_record=standing_data.get("homeRecord"),
                away_record=standing_data.get("awayRecord"),
                
                # Formatted strings
                goals_home_formatted=standing_data.get("goalsHomeFormatted"),
                goals_away_formatted=standing_data.get("goalsAwayFormatted"),
                total_goals_formatted=standing_data.get("totalGoalsFormatted"),
                
                # Additional fields
                team_penalty=standing_data.get("teamPenalty"),
                team_penalty_negative=standing_data.get("teamPenaltyNegative"),
                team_penalty_positive=standing_data.get("teamPenaltyPositive"),
                dispensation=standing_data.get("dispensation"),
                team_entry_status=standing_data.get("teamEntryStatus"),
                
                # Timestamps
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            standings_to_add.append(standing)
        
        # Add all standings to the session
        if standings_to_add:
            db.add_all(standings_to_add)
            
            try:
                db.commit()
                logger.info("Successfully saved tournament standings", extra={
                    "tournament_id": tournament_id,
                    "standings_count": len(standings_to_add)
                })
            except Exception as e:
                db.rollback()
                logger.error("Error saving tournament standings", extra={
                    "tournament_id": tournament_id,
                    "error": str(e)
                })
                raise
        else:
            logger.info("No standings to save", extra={"tournament_id": tournament_id})