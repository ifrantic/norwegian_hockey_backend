# src/scripts/fetch_standings.py
import asyncio
from sqlalchemy.orm import Session
from src.services.standing_service import StandingService
from src.utils.database import get_db
from src.models.tournament import Tournament

async def main():
    service = StandingService()
    db = next(get_db())
    
    try:
        # Get all tournament IDs from the database
        tournaments = db.query(Tournament.tournament_id).all()
        tournament_ids = [t[0] for t in tournaments]
        
        # You can filter to test with just a few tournaments first
        # tournament_ids = [429162, 429552]  # EHL og 1. div menn 2024/2025, for testing
        
        print(f"Fetching standings for {len(tournament_ids)} tournaments...")
        
        # Process tournaments in batches to avoid overwhelming the API
        batch_size = 5
        for i in range(0, len(tournament_ids), batch_size):
            batch = tournament_ids[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1} of {len(tournament_ids)//batch_size + 1}")
            
            for tournament_id in batch:
                try:
                    print(f"Fetching standings for tournament {tournament_id}")
                    data = await service.fetch_tournament_standings(tournament_id)
                    service.save_tournament_standings(db, data)
                    print(f"  Standings saved: {len(data.get('standings', []))}")
                    # Small delay to be nice to the API
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"  Error fetching standings for tournament {tournament_id}: {e}")
        
        print("Finished fetching standings")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())