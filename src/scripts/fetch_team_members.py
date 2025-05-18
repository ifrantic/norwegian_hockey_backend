import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from src.services.team_member_service import TeamMemberService
from src.utils.database import get_db
from src.models.team import Team

async def main():
    service = TeamMemberService()
    db = next(get_db())
    
    try:
        # Get all unique team IDs from the database
        team_ids_query = db.query(distinct(Team.team_id))
        team_ids = [team_id[0] for team_id in team_ids_query.all()]
        
        print(f"Found {len(team_ids)} unique teams")
        
        if not team_ids:
            print("No teams to fetch members for. Run fetch_teams first.")
            return
        
        # Process teams in batches to avoid overwhelming the API
        batch_size = 20
        for i in range(0, len(team_ids), batch_size):
            batch = team_ids[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1} of {len(team_ids)//batch_size + 1} ({len(batch)} teams)")
            
            for team_id in batch:
                try:
                    print(f"Fetching members for team {team_id}")
                    data = await service.fetch_team_members(team_id)
                    member_count = len(data.get("members", []))
                    
                    if member_count > 0:
                        service.save_team_members(db, data)
                        print(f"  Saved {member_count} team members")
                    else:
                        print(f"  No members found for team {team_id}")
                    
                    # Small delay to be nice to the API
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"  Error processing team {team_id}: {e}")
        
        print("Finished fetching team members")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())