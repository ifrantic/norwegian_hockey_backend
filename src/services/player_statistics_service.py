# src/services/player_statistics_service.py
import httpx
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import asyncio
from src.config.settings import get_settings
from src.models.player_statistic import PlayerStatistic
from src.utils.logging_config import setup_logging

logger = setup_logging("player_statistics_service")

class PlayerStatisticsService:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.API_BASE_URL

    async def fetch_tournament_players(self, tournament_id: int, max_retries: int = 3) -> list:
        """Fetch player statistics for a tournament"""
        if not isinstance(tournament_id, int) or tournament_id <= 0:
            raise ValueError(f"Invalid tournament_id: {tournament_id}")
        
        retries = 0
        logger.info(f"Fetching player statistics for tournament {tournament_id}")
        
        while retries < max_retries:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        f"{self.base_url}/icehockey/TournamentPlayers/{tournament_id}"
                    )
                    response.raise_for_status()
                    return response.json()
            
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
                    logger.error("Failed to fetch data after maximum retries", extra={
                        "tournament_id": tournament_id,
                        "retry_count": retries,
                        "error": str(e)
                    })
                    raise Exception(f"Failed to fetch player statistics after {max_retries} attempts: {str(e)}")
                await asyncio.sleep(2 ** retries)  # Exponential backoff

    def save_tournament_player_statistics(self, db: Session, tournament_id: int, data: list):
        """Save player statistics to database with duplicate handling"""
        try:
            # Delete existing statistics for this tournament to avoid duplicates
            deleted_count = db.query(PlayerStatistic).filter(
                PlayerStatistic.tournament_id == tournament_id
            ).delete()
            db.commit()
            
            if deleted_count > 0:
                logger.info(f"Deleted {deleted_count} existing player statistics for tournament {tournament_id}")
            
            # Group data by person_id to handle duplicates from API
            player_data_by_person = {}
            duplicate_count = 0
            
            for player_data in data:
                person_id = player_data.get("personId")
                if not person_id:
                    logger.warning(f"Skipping player data without personId: {player_data}")
                    continue
                    
                if person_id in player_data_by_person:
                    duplicate_count += 1
                    logger.debug(f"Duplicate person_id {person_id} found in API data for tournament {tournament_id}")
                    # Keep the first occurrence, or you could merge stats if needed
                    continue
                    
                player_data_by_person[person_id] = player_data
            
            if duplicate_count > 0:
                logger.info(f"Found {duplicate_count} duplicate person_ids in API data for tournament {tournament_id}")
            
            saved_count = 0
            error_count = 0
            
            for person_id, player_data in player_data_by_person.items():
                try:
                    player_stat = PlayerStatistic(
                        tournament_id=tournament_id,
                        person_id=player_data["personId"],
                        org_id=player_data.get("orgId", 0),
                        first_name=player_data.get("firstName", "Unknown"),
                        last_name=player_data.get("lastName", "Unknown"),
                        team_name=player_data.get("teamName", "Unknown"),
                        team_short_name=player_data.get("teamShortName"),
                        position=player_data.get("position") or None,
                        rank=player_data.get("rank"),
                        scoring_points=player_data.get("pts", 0),  # Goals + Assists (for ranking)
                        plus_minus=player_data.get("points", 0),   # +/- rating (defensive stat)
                        games_played=player_data.get("gamesPlayed", 0),
                        goals_scored=player_data.get("goalsScored", 0),
                        assists=player_data.get("assists", 0),
                        points=player_data.get("points", 0),
                        pim=player_data.get("pim", 0),
                        power_play_goals=player_data.get("powerPlayGoals", 0),
                        power_play_goal_assists=player_data.get("powerPlayGoalAssists", 0),
                        short_handed_goals=player_data.get("shortHandedGoals", 0),
                        short_handed_goal_assists=player_data.get("shortHandedGoalAssists", 0),
                        gwg=player_data.get("gwg", 0),
                        shots=player_data.get("shots", 0),
                        shots_pct=player_data.get("shotsPct"),
                        face_offs=player_data.get("faceOffs", 0),
                        faceoffs_win_pct=player_data.get("faceoffsWinPct")
                    )
                    db.add(player_stat)
                    saved_count += 1
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error creating player statistic for person_id {person_id}: {e}")
                    continue
            
            # Commit all at once
            try:
                db.commit()
                logger.info(f"Successfully saved {saved_count} player statistics for tournament {tournament_id}")
                if error_count > 0:
                    logger.warning(f"{error_count} players had errors and were skipped")
                    
            except IntegrityError as e:
                db.rollback()
                logger.error(f"Database integrity error for tournament {tournament_id}: {e}")
                # Try saving one by one to identify problematic records
                return self._save_one_by_one(db, tournament_id, list(player_data_by_person.values()))
                
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving player statistics for tournament {tournament_id}: {e}")
            raise

    def _save_one_by_one(self, db: Session, tournament_id: int, data: list):
        """Fallback method to save records one by one"""
        saved_count = 0
        error_count = 0
        
        logger.info(f"Attempting to save {len(data)} records one by one for tournament {tournament_id}")
        
        for player_data in data:
            try:
                # Check if record already exists
                existing = db.query(PlayerStatistic).filter(
                    PlayerStatistic.tournament_id == tournament_id,
                    PlayerStatistic.person_id == player_data["personId"]
                ).first()
                
                if existing:
                    logger.debug(f"Player {player_data['personId']} already exists for tournament {tournament_id}, skipping")
                    continue
                
                player_stat = PlayerStatistic(
                    tournament_id=tournament_id,
                    person_id=player_data["personId"],
                    org_id=player_data.get("orgId", 0),
                    first_name=player_data.get("firstName", "Unknown"),
                    last_name=player_data.get("lastName", "Unknown"),
                    team_name=player_data.get("teamName", "Unknown"),
                    team_short_name=player_data.get("teamShortName"),
                    position=player_data.get("position") or None,
                    rank=player_data.get("rank"),
                    pts=player_data.get("pts"),
                    games_played=player_data.get("gamesPlayed", 0),
                    goals_scored=player_data.get("goalsScored", 0),
                    assists=player_data.get("assists", 0),
                    points=player_data.get("points", 0),
                    pim=player_data.get("pim", 0),
                    power_play_goals=player_data.get("powerPlayGoals", 0),
                    power_play_goal_assists=player_data.get("powerPlayGoalAssists", 0),
                    short_handed_goals=player_data.get("shortHandedGoals", 0),
                    short_handed_goal_assists=player_data.get("shortHandedGoalAssists", 0),
                    gwg=player_data.get("gwg", 0),
                    shots=player_data.get("shots", 0),
                    shots_pct=player_data.get("shotsPct"),
                    face_offs=player_data.get("faceOffs", 0),
                    faceoffs_win_pct=player_data.get("faceoffsWinPct")
                )
                
                db.add(player_stat)
                db.commit()
                saved_count += 1
                
            except IntegrityError as e:
                db.rollback()
                error_count += 1
                logger.warning(f"Duplicate key for person_id {player_data.get('personId')} in tournament {tournament_id}")
                
            except Exception as e:
                db.rollback()
                error_count += 1
                logger.error(f"Error saving player {player_data.get('personId')}: {e}")
        
        logger.info(f"One-by-one save completed: {saved_count} saved, {error_count} errors for tournament {tournament_id}")

    def get_tournament_player_statistics(self, db: Session, tournament_id: int) -> list[PlayerStatistic]:
        """Get player statistics for a tournament"""
        return db.query(PlayerStatistic).filter(
            PlayerStatistic.tournament_id == tournament_id
        ).order_by(PlayerStatistic.rank.asc(), PlayerStatistic.points.desc()).all()

    def get_top_scorers(self, db: Session, tournament_id: int = None, limit: int = 10) -> list[PlayerStatistic]:
        """Get top scorers, optionally filtered by tournament"""
        query = db.query(PlayerStatistic)
        
        if tournament_id:
            query = query.filter(PlayerStatistic.tournament_id == tournament_id)
            
        return query.order_by(
            PlayerStatistic.points.desc(),
            PlayerStatistic.goals_scored.desc()
        ).limit(limit).all()