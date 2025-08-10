import asyncio
import logging

# Import the main functions from each script
from src.scripts.fetch_tournaments import main as fetch_tournaments_main
from src.scripts.fetch_organisations import main as fetch_organisations_main
from src.scripts.fetch_teams import main as fetch_teams_main
from src.scripts.fetch_team_members import main as fetch_team_members_main
from src.scripts.fetch_standings import main as fetch_standings_main
from src.scripts.fetch_matches import main as fetch_matches_main
from src.scripts.fetch_tournament_players import main as fetch_tournament_players_main

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Run all fetch scripts in the correct order"""
    
    scripts = [
        ("Organisations", fetch_organisations_main),
        ("Tournaments", fetch_tournaments_main),
        ("Teams", fetch_teams_main),
        ("Team Members", fetch_team_members_main),
        ("Standings", fetch_standings_main),
        ("Matches", fetch_matches_main),
        ("Tournament Player Statistics", fetch_tournament_players_main),
    ]
    
    total_scripts = len(scripts)
    
    for i, (script_name, script_func) in enumerate(scripts, 1):
        try:
            logger.info(f"[{i}/{total_scripts}] Starting {script_name}...")
            await script_func()
            logger.info(f"[{i}/{total_scripts}] ✅ {script_name} completed successfully")
            
        except Exception as e:
            logger.error(f"[{i}/{total_scripts}] ❌ {script_name} failed: {e}")
            # Continue with other scripts even if one fails
            continue
    
    logger.info("🎉 All fetch scripts completed!")

if __name__ == "__main__":
    asyncio.run(main())