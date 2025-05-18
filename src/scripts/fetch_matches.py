import asyncio
from sqlalchemy.orm import Session
from src.services.match_service import MatchService
from src.utils.database import get_db
from src.models.tournament import Tournament

async def main():
    service = MatchService()
    db = next(get_db())
    
    try:
        # Get all tournament IDs from the database
        tournaments = db.query(Tournament.tournament_id).all()
        tournament_ids = [t[0] for t in tournaments]
        # tournament_ids=[429162,429552] # EHL og 1. div menn 2024/2025 , for small test
        
        print(f"Fetching matches for {len(tournament_ids)} tournaments...")
        
        # Process tournaments in batches to avoid overwhelming the API
        batch_size = 5
        for i in range(0, len(tournament_ids), batch_size):
            batch = tournament_ids[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1} of {len(tournament_ids)//batch_size + 1}")
            
            for tournament_id in batch:
                try:
                    print(f"Fetching matches for tournament {tournament_id}")
                    data = await service.fetch_tournament_matches(tournament_id)
                    service.save_tournament_matches(db, data)
                    print(f"  Matches saved: {len(data.get('matches', []))}")
                    # Small delay to be nice to the API
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"  Error fetching matches for tournament {tournament_id}: {e}")
        
        print("Finished fetching matches")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())