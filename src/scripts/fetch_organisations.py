import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from src.services.organisation_service import OrganisationService
from src.utils.database import get_db
from src.models.team import Team

async def main():
    service = OrganisationService()
    db = next(get_db())
    
    try:
        # Get all unique organisation IDs from teams
        org_ids_query = db.query(distinct(Team.club_org_id)).filter(Team.club_org_id.isnot(None))
        org_ids = [org_id[0] for org_id in org_ids_query.all()]
        
        print(f"Found {len(org_ids)} unique organisation IDs")
        
        if not org_ids:
            print("No organisations to fetch. Run fetch_teams first.")
            return
        
        # Process organisations in batches
        batch_size = 20  # API may support more org_ids at once
        for i in range(0, len(org_ids), batch_size):
            batch = org_ids[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1} of {len(org_ids)//batch_size + 1} ({len(batch)} organisations)")
            
            try:
                # Fetch and save organisations
                data = await service.fetch_organisations(batch)
                service.save_organisations(db, data)
                print(f"  Saved {len(data['organisations'])} organisations")
                
                # Small delay to be nice to the API
                await asyncio.sleep(1)
            except Exception as e:
                print(f"  Error processing batch: {e}")
        
        print("Finished fetching organisations")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())