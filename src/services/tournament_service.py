import httpx
from datetime import datetime
from sqlalchemy.orm import Session
import asyncio
from src.config.settings import Settings
from src.models.tournament import Tournament, TournamentClass
from src.utils.logging_config import setup_logging
from datetime import datetime

# Set up logging
logger = setup_logging("tournament_service")
logger.setLevel("INFO")

class TournamentService:
    def __init__(self):
        self.settings = Settings()
        self.base_url = self.settings.API_BASE_URL

    async def fetch_season_tournaments(self, season_id: int, max_retries: int = 3) -> dict:
        if not isinstance(season_id, int) or season_id <= 0:
            raise ValueError(f"Invalid season_id: {season_id}")
        retries = 0
        logger.info(f"Fetching tournaments for season {season_id}")
        while retries < max_retries:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        f"{self.base_url}/ta/Tournament/Season/{season_id}"
                    )
                    response.raise_for_status()
                    return response.json()
            
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                retries += 1
                logger.warning("API request failed, retrying", extra={
                    "season_id": season_id,
                    "retry_count": retries,
                    "max_retries": max_retries,
                    "error": str(e),
                    "wait_seconds": 2 ** retries
                })
                if retries == max_retries:
                    logger.error("Failed to fetch data after maximum retries", extra={
                        "season_id": season_id,
                        "retry_count": retries,
                        "error": str(e)
                    })
                    raise Exception(f"Failed to fetch data after {max_retries} attempts: {str(e)}")
                await asyncio.sleep(2 ** retries)  # Exponential backoff

    def _parse_date(self, date_str: str | None) -> datetime | None:
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None

    def save_tournaments(self, db: Session, data: dict):
        for tournament_data in data.get("tournamentsInSeason", []):
            tournament = Tournament(
                tournament_id=tournament_data["tournamentId"],
                tournament_no=tournament_data["tournamentNo"],
                from_date=self._parse_date(tournament_data["fromDate"]),
                to_date=self._parse_date(tournament_data["toDate"]),
                is_archival=tournament_data["isArchival"],
                is_deleted=tournament_data["isDeleted"],
                org_id_owner=tournament_data["orgIdOwner"],
                parent_tournament_id=tournament_data["parentTournamentId"],
                season_id=tournament_data["seasonId"],
                season_name=tournament_data["seasonName"],
                tournament_name=tournament_data["tournamentName"],
                tournament_short_name=tournament_data["tournamentShortName"],
                division=tournament_data["division"],
                logo_url=tournament_data["logoUrl"],
                is_table_published=tournament_data["isTablePublished"],
                is_result_published=tournament_data["isResultPublished"],
                are_matches_published=tournament_data["areMatchesPublished"],
                publish_matches_to_date=self._parse_date(tournament_data["publishMatchesToDate"]),
                are_referees_published=tournament_data["areRefereesPublished"],
                publish_referees_to_date=self._parse_date(tournament_data["publishRefereesToDate"]),
                are_statistics_published=tournament_data["areStatisticsPublished"],
                are_teams_published=tournament_data["areTeamsPublished"],
                live_arena=tournament_data["liveArena"],
                live_client=tournament_data["liveClient"],
                withdrawals_visible=tournament_data["withdrawalsVisible"],
                team_entry=tournament_data["teamEntry"],
                tournament_type=tournament_data["tournamentType"],
                sport_id=tournament_data["sportId"]
            )
            
            for class_data in tournament_data.get("tournamentClasses", []):
                tournament_class = TournamentClass(
                    tournament_id=tournament.tournament_id,
                    class_id=class_data["classId"],
                    class_name=class_data["className"],
                    from_age=class_data["fromAge"],
                    to_age=class_data["toAge"],
                    allowed_from_age=class_data["allowedFromAge"],
                    allowed_to_age=class_data["allowedToAge"],
                    gender=class_data["gender"],
                    live_arena_storage=class_data["liveArenaStorage"]
                )
                db.merge(tournament_class)
            db.merge(tournament)
        
        db.commit()
        logger.info(f"Saved {len(data.get('tournamentsInSeason', []))} tournaments")