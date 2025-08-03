# src/services/hockey_analytics.py
from typing import Dict, Any, List, Optional
from sqlalchemy import text
from src.utils.database import get_db
from src.utils.logging_config import setup_logging
import logging

logger = setup_logging("hockey_analytics")

class HockeyAnalytics:
    def __init__(self):
        pass
    
    def _get_fresh_db(self):
        """Get a fresh database connection"""
        return next(get_db())
    
    def get_available_filters(self) -> Dict[str, Any]:
        """Get all available filter options for the frontend"""
        db = self._get_fresh_db()
        try:
            # Get active tournaments - FIX: Use table aliases
            tournaments = db.execute(text("""
                SELECT 
                    tour.tournament_id, 
                    tour.tournament_name, 
                    tour.season_name,
                    COUNT(DISTINCT t.team_id) as team_count
                FROM tournaments tour
                LEFT JOIN teams t ON tour.tournament_id = t.tournament_id
                WHERE tour.is_deleted = FALSE
                GROUP BY tour.tournament_id, tour.tournament_name, tour.season_name
                HAVING COUNT(DISTINCT t.team_id) > 0
                ORDER BY tour.tournament_name
            """)).fetchall()
            
            # Get available positions
            positions = db.execute(text("""
                SELECT DISTINCT position, COUNT(*) as count
                FROM team_members
                WHERE position IS NOT NULL
                GROUP BY position
                ORDER BY count DESC
            """)).fetchall()
            
            # Get clubs with teams
            clubs = db.execute(text("""
                SELECT DISTINCT 
                    o.org_id,
                    o.org_name, 
                    COUNT(DISTINCT t.team_id) as team_count
                FROM organisations o
                JOIN teams t ON o.org_id = t.club_org_id
                GROUP BY o.org_id, o.org_name
                ORDER BY team_count DESC, o.org_name
                LIMIT 100
            """)).fetchall()
            
            return {
                "success": True,
                "tournaments": [dict(row._mapping) for row in tournaments],
                "positions": [dict(row._mapping) for row in positions],
                "clubs": [dict(row._mapping) for row in clubs]
            }
            
        except Exception as e:
            logger.error(f"Error getting filters: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    # src/services/hockey_analytics.py
    def get_teams(self, tournament_id: Optional[int] = None, 
              club_id: Optional[int] = None,
              search: Optional[str] = None,
              limit: int = 50) -> Dict[str, Any]:
        """Get teams with smart filtering"""
        db = self._get_fresh_db()
        try:
            query = """
                SELECT DISTINCT 
                    t.team_id,
                    t.team_name,
                    COALESCE(t.overridden_name, t.team_name) AS display_name,
                    tour.tournament_name,
                    tour.season_name,
                    o.org_name AS club_name,
                    COUNT(tm.id) AS member_count,
                    COUNT(CASE WHEN tm.member_type = 'Player' THEN 1 END) AS player_count
                FROM teams t
                LEFT JOIN tournaments tour ON t.tournament_id = tour.tournament_id
                LEFT JOIN organisations o ON t.club_org_id = o.org_id
                LEFT JOIN team_members tm ON t.team_id = tm.team_id
                WHERE tour.is_deleted IS NOT TRUE
            """
            
            params = {}
            
            if tournament_id:
                query += " AND t.tournament_id = :tournament_id"
                params["tournament_id"] = tournament_id
                
            if club_id:
                query += " AND t.club_org_id = :club_id"
                params["club_id"] = club_id
                
            if search:
                query += " AND (t.team_name ILIKE :search OR t.overridden_name ILIKE :search OR o.org_name ILIKE :search)"
                params["search"] = f"%{search}%"
            
            query += """
                GROUP BY t.team_id, t.team_name, t.overridden_name, 
                        tour.tournament_name, tour.season_name, o.org_name
                ORDER BY tour.tournament_name, t.team_name
                LIMIT :limit
            """
            params["limit"] = limit
            
            result = db.execute(text(query), params)
            teams = [dict(row._mapping) for row in result.fetchall()]
            
            return {
                "success": True,
                "data": teams,
                "count": len(teams),
                "filters_applied": {
                    "tournament_id": tournament_id,
                    "club_id": club_id,
                    "search": search
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting teams: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def get_players(self, team_id: Optional[int] = None,
                position: Optional[str] = None,
                tournament_id: Optional[int] = None,
                club_id: Optional[int] = None,
                search: Optional[str] = None,
                limit: int = 100) -> Dict[str, Any]:
        """Get players with smart filters and images"""
        db = self._get_fresh_db()
        try:
            query = """
                SELECT 
                    tm.id,
                    tm.person_id,
                    tm.first_name,
                    tm.last_name,
                    tm.position,
                    tm.number,
                    tm.height,
                    tm.member_type,
                    tm.nationality,
                    tm.birth_date,
                    tm.gender,
                    t.team_name,
                    COALESCE(t.overridden_name, t.team_name) AS team_display_name,
                    tour.tournament_name,
                    o.org_name as club_name,
                    tcd.image_object_key,
                    tcd.image2_object_key,
                    tcd.original_image_url,
                    tcd.original_image2_url
                FROM team_members tm
                LEFT JOIN teams t ON tm.team_id = t.team_id
                LEFT JOIN tournaments tour ON t.tournament_id = tour.tournament_id
                LEFT JOIN organisations o ON t.club_org_id = o.org_id
                LEFT JOIN team_member_custom_data tcd ON tm.person_id = tcd.person_id
                WHERE tm.member_type = 'Player'
            """
            
            params = {}
            
            # Only filter by tournament deletion if we have tournament data
            if tournament_id:
                query += " AND tour.is_deleted IS NOT TRUE"
            else:
                query += " AND (tour.is_deleted IS NOT TRUE OR tour.is_deleted IS NULL)"
            
            if team_id:
                query += " AND tm.team_id = :team_id"
                params["team_id"] = team_id
                
            if position:
                query += " AND tm.position = :position"
                params["position"] = position
                
            if tournament_id:
                query += " AND t.tournament_id = :tournament_id"
                params["tournament_id"] = tournament_id
                
            if club_id:
                query += " AND t.club_org_id = :club_id"
                params["club_id"] = club_id
                
            if search:
                query += " AND (tm.first_name ILIKE :search OR tm.last_name ILIKE :search)"
                params["search"] = f"%{search}%"
            
            query += " ORDER BY COALESCE(tour.tournament_name, 'ZZZ'), COALESCE(t.team_name, 'ZZZ'), tm.number LIMIT :limit"
            params["limit"] = limit
            
            result = db.execute(text(query), params)
            players = [dict(row._mapping) for row in result.fetchall()]
            
            return {
                "success": True,
                "data": players,
                "count": len(players),
                "filters_applied": {
                    "team_id": team_id,
                    "position": position,
                    "tournament_id": tournament_id,
                    "club_id": club_id,
                    "search": search
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting players: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def get_insights_summary(self) -> Dict[str, Any]:
        """Get interesting insights about the data"""
        db = self._get_fresh_db()
        try:
            # Total counts - Fix: Use 'Player' not 'player'
            totals = db.execute(text("""
                SELECT 
                    (SELECT COUNT(*) FROM teams t JOIN tournaments tour ON t.tournament_id = tour.tournament_id WHERE tour.is_deleted = FALSE) as teams,
                    (SELECT COUNT(*) FROM team_members WHERE member_type = 'Player') as players,
                    (SELECT COUNT(*) FROM tournaments WHERE is_deleted = FALSE) as tournaments,
                    (SELECT COUNT(*) FROM organisations) as clubs
            """)).fetchone()
            
            # Most common positions - Fix: Use 'Player' not 'player'
            top_positions = db.execute(text("""
                SELECT position, COUNT(*) as count
                FROM team_members
                WHERE position IS NOT NULL AND member_type = 'Player'
                GROUP BY position
                ORDER BY count DESC
                LIMIT 5
            """)).fetchall()
            
            # Biggest tournaments by team count
            biggest_tournaments = db.execute(text("""
                SELECT 
                    tour.tournament_name, 
                    tour.season_name,
                    COUNT(t.team_id) as team_count
                FROM tournaments tour
                JOIN teams t ON tour.tournament_id = t.tournament_id
                WHERE tour.is_deleted = FALSE
                GROUP BY tour.tournament_id, tour.tournament_name, tour.season_name
                ORDER BY team_count DESC
                LIMIT 5
            """)).fetchall()
            
            # Clubs with most teams
            biggest_clubs = db.execute(text("""
                SELECT 
                    o.org_name,
                    COUNT(DISTINCT t.team_id) as team_count,
                    COUNT(DISTINCT t.tournament_id) as tournament_count
                FROM organisations o
                JOIN teams t ON o.org_id = t.club_org_id
                JOIN tournaments tour ON t.tournament_id = tour.tournament_id
                WHERE tour.is_deleted = FALSE
                GROUP BY o.org_id, o.org_name
                ORDER BY team_count DESC
                LIMIT 5
            """)).fetchall()
            
            return {
                "success": True,
                "totals": dict(totals._mapping) if totals else {},
                "top_positions": [dict(row._mapping) for row in top_positions],
                "biggest_tournaments": [dict(row._mapping) for row in biggest_tournaments],
                "biggest_clubs": [dict(row._mapping) for row in biggest_clubs]
            }
            
        except Exception as e:
            logger.error(f"Error getting insights: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def get_tournament_standings(self, tournament_id: int) -> Dict[str, Any]:
        """Get standings for a specific tournament"""
        db = self._get_fresh_db()
        try:
            query = """
                SELECT 
                    s.position,
                    s.team_name,
                    COALESCE(s.overridden_name, s.team_name) AS display_name,
                    s.matches_played as played,
                    s.victories as wins,
                    s.draws,
                    s.losses,
                    s.points,
                    s.goals_scored as goals_for,
                    s.goals_conceded as goals_against,
                    s.goals_diff as goal_difference,
                    CASE 
                        WHEN s.matches_played > 0 THEN ROUND((s.points::decimal / (s.matches_played * 3)) * 100, 1)
                        ELSE 0 
                    END AS points_percentage
                FROM standings s
                WHERE s.tournament_id = :tournament_id
                ORDER BY s.position ASC
            """
            
            result = db.execute(text(query), {"tournament_id": tournament_id})
            standings = [dict(row._mapping) for row in result.fetchall()]
            
            # Get tournament info
            tournament_info = db.execute(text("""
                SELECT tournament_name, season_name, tournament_type
                FROM tournaments 
                WHERE tournament_id = :tournament_id
            """), {"tournament_id": tournament_id}).fetchone()
            
            return {
                "success": True,
                "tournament": dict(tournament_info._mapping) if tournament_info else {},
                "standings": standings,
                "count": len(standings)
            }
            
        except Exception as e:
            logger.error(f"Error getting standings: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    