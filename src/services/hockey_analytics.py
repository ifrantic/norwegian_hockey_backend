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
    
    # get available filters for frontend
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
    
    # get teams with smart filtering
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
                    o.org_name AS org_name,
                    t.club_org_id AS org_id,
                    o.org_logo_base64 as logo,
                    tour.tournament_id AS tournament_id,
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
                GROUP BY t.team_id, t.team_name, t.overridden_name, o.org_logo_base64,
                        tour.tournament_name, tour.season_name, o.org_name, t.club_org_id, tour.tournament_id
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

    # get players with smart filters and images
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
                SELECT DISTINCT
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
                    o.org_name as club_name,
                    tcd.image_object_key,
                    tcd.image2_object_key,
                    t.team_id as team_id,
                    o.org_id as org_id
                FROM team_members tm
                LEFT JOIN teams t ON tm.team_id = t.team_id
                LEFT JOIN organisations o ON t.club_org_id = o.org_id
                LEFT JOIN team_member_custom_data tcd ON tm.person_id = tcd.person_id
                WHERE tm.member_type = 'Player'
            """
            
            params = {}
            
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
            
            query += " ORDER BY tm.person_id LIMIT :limit"
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


    # get standings for a specific tournament
    def get_tournament_standings(self, tournament_id: int) -> Dict[str, Any]:
        """Get standings for a specific tournament"""
        db = self._get_fresh_db()
        try:
            query = """
                SELECT distinct
                    s.id,
                    s.tournament_id,
                    s.team_id,
                    s.team_name,
                    s.overridden_name,
                    COALESCE(s.overridden_name, s.team_name) AS display_name,
                    s.position,
                    s.entry_id,
                    
                    -- Match stats
                    s.matches_played,
                    s.matches_home,
                    s.matches_away,
                    
                    -- Points
                    s.points,
                    s.points_home,
                    s.points_away,
                    s.points_start,
                    s.total_points,
                    
                    -- Victories
                    s.victories,
                    s.victories_home,
                    s.victories_away,
                    s.victories_fulltime_total,
                    s.victories_fulltime_home,
                    s.victories_fulltime_away,
                    s.victories_overtime_total,
                    s.victories_overtime_home,
                    s.victories_overtime_away,
                    s.victories_penalties_total,
                    s.victories_penalties_home,
                    s.victories_penalties_away,
                    
                    -- Draws
                    s.draws,
                    s.draws_home,
                    s.draws_away,
                    
                    -- Losses
                    s.losses,
                    s.losses_home,
                    s.losses_away,
                    s.losses_fulltime_total,
                    s.losses_fulltime_home,
                    s.losses_fulltime_away,
                    s.losses_overtime_total,
                    s.losses_overtime_home,
                    s.losses_overtime_away,
                    s.losses_penalties_total,
                    s.losses_penalties_home,
                    s.losses_penalties_away,
                    
                    -- Goals
                    s.goals_scored,
                    s.goals_scored_home,
                    s.goals_scored_away,
                    s.goals_conceded,
                    s.goals_conceded_home,
                    s.goals_conceded_away,
                    s.goals_diff,
                    s.goals_ratio,
                    
                    -- Penalty minutes
                    s.penalty_minutes,
                    
                    -- Records
                    s.home_record,
                    s.away_record,
                    
                    -- Formatted strings
                    s.goals_home_formatted,
                    s.goals_away_formatted,
                    s.total_goals_formatted,
                    
                    -- Additional fields
                    s.team_penalty,
                    s.team_penalty_negative,
                    s.team_penalty_positive,
                    s.dispensation,
                    s.team_entry_status,
                    
                    -- Metadata
                    s.created_at,
                    s.updated_at,

                    -- logo
                    o.org_logo_base64
                FROM standings s
                JOIN teams t ON t.team_id = s.team_id
                JOIN organisations o ON t.club_org_id = o.org_id
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


    # get interesting insights about the data, like small stats and summaries
    def get_insights_summary(self) -> Dict[str, Any]:
        """Get interesting insights about the data"""
        db = self._get_fresh_db()
        try:
            # Total counts 
            totals = db.execute(text("""
                SELECT 
                    (SELECT COUNT(*) FROM teams t JOIN tournaments tour ON t.tournament_id = tour.tournament_id WHERE tour.is_deleted = FALSE) as teams,
                    (SELECT COUNT(*) FROM team_members WHERE member_type = 'Player') as players,
                    (SELECT COUNT(*) FROM tournaments WHERE is_deleted = FALSE) as tournaments,
                    (SELECT COUNT(*) FROM organisations) as clubs
            """)).fetchone()
            
            # Most common positions 
            top_positions = db.execute(text("""
                SELECT position, COUNT(*) as count
                FROM team_members
                WHERE position IS NOT NULL AND member_type = 'Player'
                GROUP BY position
                ORDER BY count DESC
                LIMIT 6
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
                    COUNT(DISTINCT t.tournament_id) as tournament_count,
					o.org_logo_base64
                FROM organisations o
                JOIN teams t ON o.org_id = t.club_org_id
                JOIN tournaments tour ON t.tournament_id = tour.tournament_id
                WHERE tour.is_deleted = FALSE
                GROUP BY o.org_id, o.org_name
                ORDER BY team_count DESC
                LIMIT 5
            """)).fetchall()
            
     # Top scorers across all tournaments
            top_scorers_overall = db.execute(text("""
                SELECT 
                    ps.first_name,
                    ps.last_name,
                    ps.team_name,
                    ps.scoring_points as points,
                    ps.goals_scored,
                    ps.assists,
                    t.tournament_name
                FROM player_statistics ps
                LEFT JOIN tournaments t ON ps.tournament_id = t.tournament_id
                WHERE t.is_deleted IS NOT TRUE
                ORDER BY ps.scoring_points DESC
                LIMIT 5
            """)).fetchall()
            
            return {
                "success": True,
                "totals": dict(totals._mapping) if totals else {},
                "top_positions": [dict(row._mapping) for row in top_positions],
                "biggest_tournaments": [dict(row._mapping) for row in biggest_tournaments],
                "biggest_clubs": [dict(row._mapping) for row in biggest_clubs],
                "top_scorers": [dict(row._mapping) for row in top_scorers_overall]  # ADD this
            }
            
        except Exception as e:
            logger.error(f"Error getting insights: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()


    ######## tournament player statistics ########
    # src/services/hockey_analytics.py
    def get_tournament_player_stats(self, tournament_id: int, 
                                stat_type: str = "points",
                                limit: int = 20) -> Dict[str, Any]:
        """Get player statistics for a tournament"""
        db = self._get_fresh_db()
        try:
            # Determine ordering based on stat_type
            order_columns = {
                "points": "ps.scoring_points DESC, ps.goals_scored DESC",
                "goals": "ps.goals_scored DESC, ps.scoring_points DESC", 
                "assists": "ps.assists DESC, ps.scoring_points DESC",
                "plus_minus": "ps.plus_minus DESC",
                "pim": "ps.pim DESC",
                "shots": "ps.shots DESC",
                "rank": "ps.rank ASC"
            }

            order_by = order_columns.get(stat_type, "ps.rank ASC")

            query = f"""
                SELECT 
                    ps.id,
                    ps.person_id,
                    ps.first_name,
                    ps.last_name,
                    ps.team_name,
                    ps.team_short_name,
                    ps.position,
                    ps.rank,
                    ps.games_played,
                    ps.goals_scored,
                    ps.assists,
                    ps.scoring_points,
                    ps.plus_minus,
                    ps.pim,
                    ps.power_play_goals,
                    ps.power_play_goal_assists,
                    ps.short_handed_goals,
                    ps.short_handed_goal_assists,
                    ps.gwg,
                    ps.shots,
                    ps.shots_pct,
                    ps.face_offs,
                    ps.faceoffs_win_pct,
                    ps.org_id,
                    -- Player demographics
                    tm.birth_date,
                    tm.gender,
                    tm.nationality,
                    -- Images
                    tcd.image_object_key,
                    tcd.image2_object_key
                FROM player_statistics ps
                LEFT JOIN team_members tm ON ps.person_id = tm.person_id
                LEFT JOIN team_member_custom_data tcd ON ps.person_id = tcd.person_id
                WHERE ps.tournament_id = :tournament_id
                ORDER BY {order_by}
                LIMIT :limit
            """
            
            result = db.execute(text(query), {
                "tournament_id": tournament_id,
                "limit": limit
            })
            stats = [dict(row._mapping) for row in result.fetchall()]
            
            # Get tournament info
            tournament_info = db.execute(text("""
                SELECT tournament_name, season_name, tournament_type
                FROM tournaments 
                WHERE tournament_id = :tournament_id
            """), {"tournament_id": tournament_id}).fetchone()
            
            return {
                "success": True,
                "tournament": dict(tournament_info._mapping) if tournament_info else {},
                "stat_type": stat_type,
                "data": stats,
                "count": len(stats)
            }
            
        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def get_top_scorers_overall(self, stat_type: str = "points", 
                            position: Optional[str] = None,
                            limit: int = 50) -> Dict[str, Any]:
        """Get top scorers across all tournaments"""
        db = self._get_fresh_db()
        try:
            # Determine ordering based on stat_type
            order_columns = {
                "points": "ps.scoring_points DESC, ps.goals_scored DESC",
                "goals": "ps.goals_scored DESC, ps.scoring_points DESC", 
                "assists": "ps.assists DESC, ps.scoring_points DESC",
                "pim": "ps.pim DESC",
                "shots": "ps.shots DESC",
                "saves": "ps.shots_pct DESC",
                "faceoffs": "ps.faceoffs_win_pct DESC"
            }
            
            order_by = order_columns.get(stat_type, "ps.scoring_points DESC, ps.goals_scored DESC")
            
            query = f"""
                SELECT 
                    ps.id,
                    ps.person_id,
                    ps.first_name,
                    ps.last_name,
                    ps.team_name,
                    ps.team_short_name,
                    ps.position,
                    ps.rank,
                    ps.games_played,
                    ps.goals_scored,
                    ps.assists,
                    ps.scoring_points,
                    ps.plus_minus,
                    ps.pim,
                    ps.power_play_goals,
                    ps.power_play_goal_assists,
                    ps.short_handed_goals,
                    ps.short_handed_goal_assists,
                    ps.gwg,
                    ps.shots,
                    ps.shots_pct,
                    ps.face_offs,
                    ps.faceoffs_win_pct,
                    ps.org_id,
                    ps.tournament_id,
                    -- Tournament info
                    t.tournament_name,
                    t.season_name,
                    -- Player demographics
                    tm.birth_date,
                    tm.gender,
                    tm.nationality,
                    -- Images
                    tcd.image_object_key,
                    tcd.image2_object_key,
                    tcd.original_image_url,
                    tcd.original_image2_url
                FROM player_statistics ps
                LEFT JOIN tournaments t ON ps.tournament_id = t.tournament_id
                LEFT JOIN team_members tm ON ps.person_id = tm.person_id
                LEFT JOIN team_member_custom_data tcd ON ps.person_id = tcd.person_id
                WHERE t.is_deleted IS NOT TRUE
            """
            
            params = {"limit": limit}
            
            if position:
                query += " AND ps.position = :position"
                params["position"] = position
                
            query += f" ORDER BY {order_by} LIMIT :limit"
            
            result = db.execute(text(query), params)
            stats = [dict(row._mapping) for row in result.fetchall()]
            
            return {
                "success": True,
                "stat_type": stat_type,
                "position_filter": position,
                "data": stats,
                "count": len(stats)
            }
            
        except Exception as e:
            logger.error(f"Error getting top scorers: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def get_player_career_stats(self, person_id: int) -> Dict[str, Any]:
        """Get career statistics for a specific player across all tournaments"""
        db = self._get_fresh_db()
        try:
            # Individual tournament stats
            tournament_stats = db.execute(text("""
                SELECT 
                    ps.tournament_id,
                    t.tournament_name,
                    t.season_name,
                    ps.team_name,
                    ps.team_short_name,
                    ps.position,
                    ps.rank,
                    ps.games_played,
                    ps.goals_scored,
                    ps.assists,
                    ps.scoring_points,
                    ps.plus_minus,
                    ps.pim,
                    ps.power_play_goals,
                    ps.power_play_goal_assists,
                    ps.short_handed_goals,
                    ps.short_handed_goal_assists,
                    ps.gwg,
                    ps.shots,
                    ps.shots_pct,
                    ps.face_offs,
                    ps.faceoffs_win_pct,
                    -- Player demographics
                    tm.birth_date,
                    tm.gender,
                    tm.nationality
                FROM player_statistics ps
                LEFT JOIN tournaments t ON ps.tournament_id = t.tournament_id
                LEFT JOIN team_members tm ON ps.person_id = tm.person_id
                WHERE ps.person_id = :person_id
                ORDER BY t.season_name DESC, ps.scoring_points DESC
            """), {"person_id": person_id}).fetchall()
            
            # Career totals
            career_totals = db.execute(text("""
                SELECT 
                    ps.first_name,
                    ps.last_name,
                    COUNT(DISTINCT ps.tournament_id) as tournaments_played,
                    SUM(ps.games_played) as total_games,
                    SUM(ps.goals_scored) as total_goals,
                    SUM(ps.assists) as total_assists,
                    SUM(ps.scoring_points) as total_points,
                    SUM(ps.pim) as total_pim,
                    SUM(ps.power_play_goals) as total_pp_goals,
                    SUM(ps.power_play_goal_assists) as total_pp_assists,
                    SUM(ps.short_handed_goals) as total_sh_goals,
                    SUM(ps.short_handed_goal_assists) as total_sh_assists,
                    SUM(ps.gwg) as total_gwg,
                    SUM(ps.shots) as total_shots,
                    CASE 
                        WHEN SUM(ps.shots) > 0 THEN ROUND((SUM(ps.goals_scored)::decimal / SUM(ps.shots)) * 100, 2)
                        ELSE 0 
                    END as career_shot_pct,
                    SUM(ps.face_offs) as total_faceoffs,
                    -- Player demographics (take first non-null values)
                    MAX(tm.birth_date) as birth_date,
                    MAX(tm.gender) as gender,
                    MAX(tm.nationality) as nationality,
                    -- Images
                    tcd.image_object_key,
                    tcd.image2_object_key,
                    tcd.original_image_url,
                    tcd.original_image2_url
                FROM player_statistics ps
                LEFT JOIN team_members tm ON ps.person_id = tm.person_id
                LEFT JOIN team_member_custom_data tcd ON ps.person_id = tcd.person_id
                WHERE ps.person_id = :person_id
                GROUP BY ps.person_id, ps.first_name, ps.last_name, 
                        tcd.image_object_key, tcd.image2_object_key, 
                        tcd.original_image_url, tcd.original_image2_url
            """), {"person_id": person_id}).fetchone()
            
            return {
                "success": True,
                "player_info": dict(career_totals._mapping) if career_totals else {},
                "tournament_stats": [dict(row._mapping) for row in tournament_stats],
                "tournaments_count": len(tournament_stats)
            }
            
        except Exception as e:
            logger.error(f"Error getting player career stats: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()


 # src/services/hockey_analytics.py
    def get_player_stats_summary(self, tournament_id: Optional[int] = None) -> Dict[str, Any]:
        """Get summary statistics about player performance"""
        db = self._get_fresh_db()
        try:
            base_where = "WHERE t.is_deleted IS NOT TRUE"
            params = {}
            
            if tournament_id:
                base_where += " AND ps.tournament_id = :tournament_id"
                params["tournament_id"] = tournament_id
            
            # Top performers by category - FIXED: Use scoring_points
            top_scorers = db.execute(text(f"""
                SELECT ps.first_name
                , ps.last_name
                , ps.team_name
                , ps.scoring_points
                , ps.goals_scored
                , ps.assists
                , tm.birth_date
                , tm.gender
                , tm.nationality
                FROM player_statistics ps
                LEFT JOIN team_members tm ON ps.person_id = tm.person_id
                LEFT JOIN tournaments t ON ps.tournament_id = t.tournament_id
                {base_where}
                ORDER BY ps.scoring_points DESC
                LIMIT 5
            """), params).fetchall()
            
            # Top goal scorers - FIXED: Use scoring_points
            top_goal_scorers = db.execute(text(f"""
                SELECT ps.first_name
                , ps.last_name
                , ps.team_name
                , ps.goals_scored
                , ps.scoring_points
                , ps.assists
                , tm.birth_date
                , tm.gender
                , tm.nationality
                FROM player_statistics ps
                LEFT JOIN team_members tm ON ps.person_id = tm.person_id
                LEFT JOIN tournaments t ON ps.tournament_id = t.tournament_id
                {base_where}
                ORDER BY ps.goals_scored DESC
                LIMIT 5
            """), params).fetchall()
            
            # Position breakdown - FIXED: Use scoring_points
            position_stats = db.execute(text(f"""
                SELECT 
                    ps.position,
                    COUNT(*) as player_count,
                    AVG(ps.scoring_points) as avg_points,
                    AVG(ps.goals_scored) as avg_goals,
                    AVG(ps.assists) as avg_assists
                FROM player_statistics ps
                LEFT JOIN tournaments t ON ps.tournament_id = t.tournament_id
                {base_where} AND ps.position IS NOT NULL
                GROUP BY ps.position
                ORDER BY avg_points DESC
            """), params).fetchall()
            
            # Overall stats - FIXED: Use scoring_points
            overall_stats = db.execute(text(f"""
                SELECT 
                    COUNT(DISTINCT ps.person_id) as unique_players,
                    COUNT(*) as total_player_records,
                    AVG(ps.scoring_points) as avg_points_per_player,
                    AVG(ps.goals_scored) as avg_goals_per_player,
                    AVG(ps.games_played) as avg_games_per_player,
                    MAX(ps.scoring_points) as highest_points,
                    MAX(ps.goals_scored) as highest_goals
                FROM player_statistics ps
                LEFT JOIN tournaments t ON ps.tournament_id = t.tournament_id
                {base_where}
            """), params).fetchone()
            
            return {
                "success": True,
                "tournament_id": tournament_id,
                "overall_stats": dict(overall_stats._mapping) if overall_stats else {},
                "top_scorers": [dict(row._mapping) for row in top_scorers],
                "top_goal_scorers": [dict(row._mapping) for row in top_goal_scorers],
                "position_breakdown": [dict(row._mapping) for row in position_stats]
            }
            
        except Exception as e:
            logger.error(f"Error getting player stats summary: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    # ADD: The ranking analysis method
    def analyze_tournament_ranking_system(self, tournament_id: int) -> Dict[str, Any]:
        """Analyze how rankings are determined in a tournament"""
        db = self._get_fresh_db()
        try:
            # Get top 15 by official ranking
            ranked_players = db.execute(text("""
                SELECT 
                    ps.rank,
                    ps.person_id,
                    ps.first_name,
                    ps.last_name,
                    ps.team_name,
                    ps.games_played,
                    ps.goals_scored,
                    ps.assists,
                    ps.scoring_points,
                    ps.plus_minus,
                    ps.pts as api_pts,
                    CASE 
                        WHEN ps.games_played > 0 THEN ROUND(ps.scoring_points::decimal / ps.games_played, 3)
                        ELSE 0 
                    END as points_per_game,
                    ps.shots,
                    ps.shots_pct,
                    -- Player demographics
                    tm.birth_date,
                    tm.gender,
                    tm.nationality
                FROM player_statistics ps
                LEFT JOIN team_members tm ON ps.person_id = tm.person_id
                WHERE ps.tournament_id = :tournament_id
                ORDER BY ps.rank ASC NULLS LAST
                LIMIT 15
            """), {"tournament_id": tournament_id}).fetchall()
            
            # Get top 10 by pure scoring points
            points_leaders = db.execute(text("""
                SELECT 
                    ps.rank,
                    ps.person_id,
                    ps.first_name,
                    ps.last_name,
                    ps.scoring_points,
                    ps.goals_scored,
                    ps.assists,
                    ps.games_played,
                    -- Player demographics
                    tm.birth_date,
                    tm.gender,
                    tm.nationality
                FROM player_statistics ps
                LEFT JOIN team_members tm ON ps.person_id = tm.person_id
                WHERE ps.tournament_id = :tournament_id
                ORDER BY ps.scoring_points DESC, ps.goals_scored DESC
                LIMIT 10
            """), {"tournament_id": tournament_id}).fetchall()
            
            return {
                "success": True,
                "tournament_id": tournament_id,
                "official_rankings": [dict(row._mapping) for row in ranked_players],
                "pure_points_leaders": [dict(row._mapping) for row in points_leaders],
                "analysis": {
                    "rank_1_player": dict(ranked_players[0]._mapping) if ranked_players else None,
                    "points_leader": dict(points_leaders[0]._mapping) if points_leaders else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing rankings: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()
            """Analyze how rankings are determined in a tournament"""
            db = self._get_fresh_db()
            try:
                # Get top 15 by official ranking
                ranked_players = db.execute(text("""
                    SELECT 
                        ps.rank,
                        ps.person_id,
                        ps.first_name,
                        ps.last_name,
                        ps.team_name,
                        ps.games_played,
                        ps.goals_scored,
                        ps.assists,
                        ps.scoring_points,
                        ps.plus_minus,
                        ps.pts as api_pts,
                        CASE 
                            WHEN ps.games_played > 0 THEN ROUND(ps.scoring_points::decimal / ps.games_played, 3)
                            ELSE 0 
                        END as points_per_game,
                        ps.shots,
                        ps.shots_pct
                    FROM player_statistics ps
                    WHERE ps.tournament_id = :tournament_id
                    ORDER BY ps.rank ASC NULLS LAST
                    LIMIT 15
                """), {"tournament_id": tournament_id}).fetchall()
                
                # Get top 10 by pure scoring points
                points_leaders = db.execute(text("""
                    SELECT 
                        ps.rank,
                        ps.person_id,
                        ps.first_name,
                        ps.last_name,
                        ps.scoring_points,
                        ps.goals_scored,
                        ps.assists,
                        ps.games_played
                    FROM player_statistics ps
                    WHERE ps.tournament_id = :tournament_id
                    ORDER BY ps.scoring_points DESC, ps.goals_scored DESC
                    LIMIT 10
                """), {"tournament_id": tournament_id}).fetchall()
                
                return {
                    "success": True,
                    "tournament_id": tournament_id,
                    "official_rankings": [dict(row._mapping) for row in ranked_players],
                    "pure_points_leaders": [dict(row._mapping) for row in points_leaders],
                    "analysis": {
                        "rank_1_player": dict(ranked_players[0]._mapping) if ranked_players else None,
                        "points_leader": dict(points_leaders[0]._mapping) if points_leaders else None
                    }
                }
                
            except Exception as e:
                logger.error(f"Error analyzing rankings: {e}")
                return {"success": False, "error": str(e)}
            finally:
                db.close()