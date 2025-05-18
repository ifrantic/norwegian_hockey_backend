import httpx
from datetime import datetime
from sqlalchemy.orm import Session
import asyncio
from src.config.settings import Settings
from src.models.match import Match
from src.utils.logging_config import setup_logging

# Set up logging
logger = setup_logging("match_service")

class MatchService:
    def __init__(self):
        self.settings = Settings()
        self.base_url = self.settings.API_BASE_URL

    async def fetch_tournament_matches(self, tournament_id: int, max_retries: int = 3) -> dict:
        """Fetch all matches for a given tournament"""
        if not isinstance(tournament_id, int) or tournament_id <= 0:
            raise ValueError(f"Invalid tournament_id: {tournament_id}")
            
        retries = 0
        logger.info("Fetching tournament matches", extra={
            "tournament_id": tournament_id,
            "retry_count": retries,
            "max_retries": max_retries
        })
        
        while retries < max_retries:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        f"{self.base_url}/ta/TournamentMatches/?tournamentId={tournament_id}"
                    )
                    response.raise_for_status()
                    data = response.json()
                    match_count = len(data.get("matches", []))
                    logger.info("Successfully fetched matches", extra={
                        "tournament_id": tournament_id,
                        "match_count": match_count
                    })
                    return data
            
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
                    logger.error("Failed to fetch matches after maximum retries", extra={
                        "tournament_id": tournament_id,
                        "retry_count": retries,
                        "error": str(e)
                    })
                    raise Exception(f"Failed to fetch matches after {max_retries} attempts: {str(e)}")
                    
                await asyncio.sleep(2 ** retries)  # Exponential backoff

    def _parse_date(self, date_str: str | None) -> datetime | None:
        """Parse a date string to a datetime object"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None

    def save_tournament_matches(self, db: Session, data: dict):
        """Save tournament matches to the database"""
        tournament_id = data["tournamentId"]
        
        # First, delete existing matches for this tournament to avoid duplicates
        db.query(Match).filter(Match.tournament_id == tournament_id).delete()
        
        # Commit the delete operation before adding new matches
        db.commit()
        
        matches_to_add = []
        for match_data in data.get("matches", []):
            # Extract match result data if available
            match_result = match_data.get("matchResult", {})
            
            match = Match(
                match_id=match_data["matchId"],
                tournament_id=tournament_id,
                match_no=match_data.get("matchNo"),
                activity_area_id=match_data.get("activityAreaId"),
                activity_area_latitude=match_data.get("activityAreaLatitude"),
                activity_area_longitude=match_data.get("activityAreaLongitude"),
                activity_area_name=match_data.get("activityAreaName"),
                activity_area_no=match_data.get("activityAreaNo"),
                adm_org_id=match_data.get("admOrgId"),
                arr_org_id=match_data.get("arrOrgId"),
                arr_org_no=match_data.get("arrOrgNo"),
                arr_org_name=match_data.get("arrOrgName"),
                awayteam_id=match_data.get("awayteamId"),
                awayteam_org_no=match_data.get("awayteamOrgNo"),
                awayteam=match_data.get("awayteam"),
                awayteam_org_name=match_data.get("awayteamOrgName"),
                awayteam_overridden_name=match_data.get("awayteamOverriddenName"),
                awayteam_club_org_id=match_data.get("awayteamClubOrgId"),
                hometeam_id=match_data.get("hometeamId"),
                hometeam=match_data.get("hometeam"),
                hometeam_org_name=match_data.get("hometeamOrgName"),
                hometeam_overridden_name=match_data.get("hometeamOverriddenName"),
                hometeam_org_no=match_data.get("hometeamOrgNo"),
                hometeam_club_org_id=match_data.get("hometeamClubOrgId"),
                round_id=match_data.get("roundId"),
                round_name=match_data.get("roundName"),
                season_id=match_data.get("seasonId"),
                tournament_name=match_data.get("tournamentName"),
                match_date=self._parse_date(match_data.get("matchDate")),
                match_start_time=match_data.get("matchStartTime"),
                match_end_time=match_data.get("matchEndTime"),
                venue_unit_id=match_data.get("venueUnitId"),
                venue_unit_no=match_data.get("venueUnitNo"),
                venue_id=match_data.get("venueId"),
                venue_no=match_data.get("venueNo"),
                physical_area_id=match_data.get("physicalAreaId"),
                home_goals=match_result.get("homeGoals"),
                away_goals=match_result.get("awayGoals"),
                match_end_result=match_result.get("matchEndResult"),
                live_arena=match_data.get("liveArena"),
                live_client_type=match_data.get("liveClientType"),
                status_type_id=match_data.get("statusTypeId"),
                status_type=match_data.get("statusType"),
                last_change_date=self._parse_date(match_data.get("lastChangeDate")),
                spectators=match_data.get("spectators"),
                actual_match_date=self._parse_date(match_data.get("actualMatchDate")),
                actual_match_start_time=match_data.get("actualMatchStartTime"),
                actual_match_end_time=match_data.get("actualMatchEndTime"),
                sport_id=match_data.get("sportId"),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            matches_to_add.append(match)
        
        # Add all matches to the session
        db.add_all(matches_to_add)
        
        try:
            db.commit()
            logger.info("Successfully saved tournament matches", extra={
                "tournament_id": tournament_id,
                "match_count": len(matches_to_add)
            })
        except Exception as e:
            db.rollback()
            logger.error("Error saving tournament matches", extra={
                "tournament_id": tournament_id,
                "error": str(e)
            })
            raise