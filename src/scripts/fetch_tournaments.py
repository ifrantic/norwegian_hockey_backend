import asyncio
from src.services.tournament_service import TournamentService
from src.utils.database import get_db

async def main():
    service = TournamentService()
    season_id = 201036  # Example season ID
    
    try:
        data = await service.fetch_season_tournaments(season_id)
        db = next(get_db())
        service.save_tournaments(db, data)
        print(f"Successfully fetched and saved tournaments for season {season_id}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())