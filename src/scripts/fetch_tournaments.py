import asyncio
from src.services.tournament_service import TournamentService
from src.utils.database import get_db
import json

async def main():
    service = TournamentService()
    season_id = 201036  # 201036 season ID, 2024/2025 season
    # 2025/2026 season is 201059
    
    try:
        data = await service.fetch_season_tournaments(season_id)

        db = next(get_db())
 
        # Filter to only save specific tournaments in testphase
        # comment out this in production
        # target_tournament_ids = [429552, 430746, 430748, 435748]
        #         # Filter the data to only include the target tournaments
        # filtered_data = {
        #     "seasonId": data["seasonId"],
        #     "seasonName": data["seasonName"],
        #     "tournamentsInSeason": [t for t in data["tournamentsInSeason"] if t.get("tournamentId") in target_tournament_ids]
        # }
        # service.save_tournaments(db, filtered_data)

        # uncomment this in production
        service.save_tournaments(db, data)
        print(f"Successfully fetched and saved tournaments for season {season_id}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())