# src/scripts/fetch_teams.py
import asyncio
from sqlalchemy.orm import Session
from src.services.team_service import TeamService
from src.utils.database import get_db
from src.models.tournament import Tournament

async def main():
    service = TeamService()
    db = next(get_db())
    
    try:
        # Get all tournament IDs from the database
        tournaments = db.query(Tournament.tournament_id).all()
        tournament_ids = [t[0] for t in tournaments]
        
        print(f"Fetching teams for {len(tournament_ids)} tournaments...")
        
        # Process tournaments in batches to avoid overwhelming the API
        batch_size = 10
        for i in range(0, len(tournament_ids), batch_size):
            batch = tournament_ids[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1} of {len(tournament_ids)//batch_size + 1}")
            
            for tournament_id in batch:
                try:
                    print(f"Fetching teams for tournament {tournament_id}")
                    data = await service.fetch_tournament_teams(tournament_id)
                    service.save_tournament_teams(db, data)
                    print(f"  Teams saved: {len(data.get('teams', []))}")
                    # Small delay to be nice to the API
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"  Error fetching teams for tournament {tournament_id}: {e}")
        
        print("Finished fetching teams")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())