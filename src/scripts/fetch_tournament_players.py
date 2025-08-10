# src/scripts/fetch_tournament_players.py
import asyncio
from sqlalchemy.orm import Session
from src.services.player_statistics_service import PlayerStatisticsService
from src.utils.database import get_db
from src.models.tournament import Tournament

async def main():
    service = PlayerStatisticsService()
    db = next(get_db())
    
    try:
        # Get all tournament IDs from the database
        tournaments = db.query(Tournament.tournament_id, Tournament.tournament_name).filter(
            Tournament.is_deleted == False
        ).all()
        
        print(f"Fetching player statistics for {len(tournaments)} tournaments...")
        
        success_count = 0
        error_count = 0
        empty_count = 0
        
        # Process tournaments in batches to avoid overwhelming the API
        batch_size = 5  # Smaller batch size for player stats (more data per request)
        for i in range(0, len(tournaments), batch_size):
            batch = tournaments[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1} of {(len(tournaments)-1)//batch_size + 1}")
            
            for tournament_id, tournament_name in batch:
                try:
                    print(f"Fetching player statistics for tournament {tournament_id} ({tournament_name})")
                    data = await service.fetch_tournament_players(tournament_id)
                    
                    if data and len(data) > 0:
                        service.save_tournament_player_statistics(db, tournament_id, data)
                        print(f"  ✓ Player statistics saved: {len(data)}")
                        success_count += 1
                    else:
                        print(f"  - No player statistics found")
                        empty_count += 1
                    
                    # Delay to be nice to the API
                    await asyncio.sleep(1.0)
                    
                except Exception as e:
                    error_count += 1
                    print(f"  ✗ Error fetching player statistics for tournament {tournament_id}: {e}")
            
            # Brief pause between batches
            if i + batch_size < len(tournaments):
                print("  Pausing between batches...")
                await asyncio.sleep(2.0)
        
        print("\n" + "="*60)
        print("SUMMARY:")
        print(f"  Successful: {success_count}")
        print(f"  Empty/No data: {empty_count}")
        print(f"  Errors: {error_count}")
        print(f"  Total processed: {len(tournaments)}")
        print("="*60)
        
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())