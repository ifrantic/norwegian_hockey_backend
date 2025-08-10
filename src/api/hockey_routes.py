# src/api/hockey_routes.py
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
from src.services.hockey_analytics import HockeyAnalytics
# from src.services.image_service import ImageService  # You'll need to create this

router = APIRouter()

@router.get("/")
async def hockey_root():
    """Hockey Analytics API root"""
    return {
        "message": "Norwegian Hockey Analytics API",
        "version": "1.0.0",
        "endpoints": {
            "filters": "/filters - Get available filter options",
            "teams": "/teams - Get teams with filtering",
            "players": "/players - Get players with filtering", 
            "standings": "/tournaments/{id}/standings - Get tournament standings",
            "insights": "/insights - Get data insights"
        }
    }

@router.get("/filters")
async def get_available_filters():
    """
    Get all available filter options for teams, players, etc.
    Use this to populate dropdowns and understand what data is available.
    """
    try:
        analytics = HockeyAnalytics()
        return analytics.get_available_filters()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teams")
async def get_teams(
    tournament_id: Optional[int] = Query(None, description="Filter by tournament ID"),
    club_id: Optional[int] = Query(None, description="Filter by club/organisation ID"),
    search: Optional[str] = Query(None, description="Search team names"),
    limit: int = Query(50, ge=1, le=200, description="Max results to return")
):
    """
    Get teams with smart filtering options.
    Use /filters endpoint to see available tournament_id and club_id values.
    """
    try:
        analytics = HockeyAnalytics()
        return analytics.get_teams(tournament_id, club_id, search, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/players")
async def get_players(
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    position: Optional[str] = Query(None, description="Filter by position (use /filters to see options)"),
    tournament_id: Optional[int] = Query(None, description="Filter by tournament ID"),
    club_id: Optional[int] = Query(None, description="Filter by club ID"),
    search: Optional[str] = Query(None, description="Search player names"),
    limit: int = Query(100, ge=1, le=500, description="Max results to return")
):
    """
    Get players with smart filtering options.
    Use /filters endpoint to see available values for position, tournament_id, etc.
    """
    try:
        analytics = HockeyAnalytics()
        return analytics.get_players(team_id, position, tournament_id, club_id, search, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tournaments/{tournament_id}/standings")
async def get_tournament_standings(tournament_id: int):
    """
    Get standings/table for a specific tournament.
    Use /filters endpoint to see available tournament IDs.
    """
    try:
        analytics = HockeyAnalytics()
        return analytics.get_tournament_standings(tournament_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights")
async def get_insights():
    """
    Get interesting insights and statistics about the hockey data.
    Shows totals, most common positions, biggest tournaments, etc.
    """
    try:
        analytics = HockeyAnalytics()
        return analytics.get_insights_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# get image for player
# @router.get("/players/{person_id}/image")
# async def get_player_image(person_id: int, image_type: str = Query("primary", description="primary or secondary")):
#     """
#     Get player image from MinIO storage.
#     image_type: 'primary' or 'secondary'
#     """
#     try:
#         image_service = ImageService()  # You'll need to create this service
#         image_stream = image_service.get_player_image(person_id, image_type)
        
#         if not image_stream:
#             raise HTTPException(status_code=404, detail="Image not found")
            
#         return StreamingResponse(image_stream, media_type="image/jpeg")
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

## player statistics
@router.get("/tournaments/{tournament_id}/players")
async def get_tournament_player_statistics(
    tournament_id: int,
    stat_type: str = Query("points", description="Type of stats to sort by: points, goals, assists, pim, shots, saves, faceoffs"),
    limit: int = Query(20, ge=1, le=100, description="Max results to return")
):
    """
    Get player statistics for a specific tournament.
    
    **stat_type options:**
    - points: Total points (goals + assists)
    - goals: Goals scored
    - assists: Assists
    - pim: Penalty minutes
    - shots: Shots taken
    - saves: Shooting percentage (best)
    - faceoffs: Face-off win percentage (best)
    """
    try:
        analytics = HockeyAnalytics()
        return analytics.get_tournament_player_stats(tournament_id, stat_type, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/players/top-scorers")
async def get_top_scorers_overall(
    stat_type: str = Query("points", description="Type of stats to sort by: points, goals, assists, pim, shots, saves, faceoffs"),
    position: Optional[str] = Query(None, description="Filter by player position"),
    limit: int = Query(50, ge=1, le=200, description="Max results to return")
):
    """
    Get top scorers across all tournaments.
    
    **stat_type options:**
    - points: Total points (goals + assists)
    - goals: Goals scored
    - assists: Assists
    - pim: Penalty minutes
    - shots: Shots taken
    - saves: Shooting percentage (best)
    - faceoffs: Face-off win percentage (best)
    
    **Common positions:** F, D, LW, RW, C, G
    """
    try:
        analytics = HockeyAnalytics()
        return analytics.get_top_scorers_overall(stat_type, position, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/players/{person_id}/career")
async def get_player_career_statistics(person_id: int):
    """
    Get career statistics for a specific player across all tournaments.
    Includes tournament-by-tournament breakdown and career totals.
    """
    try:
        analytics = HockeyAnalytics()
        return analytics.get_player_career_stats(person_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/players/summary")
async def get_player_statistics_summary(
    tournament_id: Optional[int] = Query(None, description="Filter by specific tournament")
):
    """
    Get summary statistics about player performance.
    Includes top performers, position breakdowns, and overall stats.
    """
    try:
        analytics = HockeyAnalytics()
        return analytics.get_player_stats_summary(tournament_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))