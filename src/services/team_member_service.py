import httpx
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.config.settings import Settings
from src.models.team_member import TeamMember
from src.utils.logging_config import setup_logging
from datetime import datetime, date
from src.services.team_member_image_service import PersonImageService


# Set up logging
logger = setup_logging("team_member_service")

class TeamMemberService:
    def __init__(self):
        self.settings = Settings()
        self.base_url = self.settings.API_BASE_URL
        self.person_image_service = PersonImageService() # for getting the images, due to jwt in urls

    
    async def fetch_team_members(self, team_id: int, max_retries: int = 3) -> Dict[str, Any]:
        """Fetch members (players, coaches) for a specific team"""
        if not isinstance(team_id, int) or team_id <= 0:
            raise ValueError(f"Invalid team_id: {team_id}")
            
        retries = 0
        logger.info("Fetching team members", extra={
            "team_id": team_id,
            "retry_count": retries,
            "max_retries": max_retries
        })
        
        while retries < max_retries:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        f"{self.base_url}/ta/TeamMembers/{team_id}"
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # Make sure we got a list back
                    if not isinstance(data, list):
                        data = [data] if data else []
                        
                    logger.info("Successfully fetched team members", extra={
                        "team_id": team_id,
                        "member_count": len(data)
                    })
                    return {"team_id": team_id, "members": data}
            
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                retries += 1
                logger.warning("API request failed, retrying", extra={
                    "team_id": team_id,
                    "retry_count": retries,
                    "max_retries": max_retries,
                    "error": str(e),
                    "wait_seconds": 2 ** retries
                })
                
                if retries == max_retries:
                    logger.error("Failed to fetch team members after maximum retries", extra={
                        "team_id": team_id,
                        "retry_count": retries,
                        "error": str(e)
                    })
                    raise Exception(f"Failed to fetch team members after {max_retries} attempts: {str(e)}")
                    
                await asyncio.sleep(2 ** retries)  # Exponential backoff
    
    def _parse_date(self, date_str: str | None) -> date | None:
        """Parse a date string to a date object"""
        if not date_str:
            return None
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.date()
        except (ValueError, AttributeError):
            return None
    
    def save_team_members(self, db: Session, data: Dict[str, Any]) -> None:
        """Save team members to the database"""
        team_id = data["team_id"]
        
        # Delete existing team members for this team to avoid duplicates
        db.query(TeamMember).filter(TeamMember.team_id == team_id).delete()
        db.commit()
        
        members_to_add = []
        image_tasks = [] # store image download tasks

        for member_data in data.get("members", []):
            person_id = member_data.get("personId")
            if not person_id:
                logger.warning("Member data missing personId", extra={
                    "team_id": team_id,
                    "member_data": str(member_data)[:100] + "..."
                })
                continue
                
            member = TeamMember(
                person_id=person_id,
                team_id=team_id,
                first_name=member_data.get("firstName"),
                last_name=member_data.get("lastName"),
                nationality=member_data.get("nationality"),
                birth_date=self._parse_date(member_data.get("birthDate")),
                gender=member_data.get("gender"),
                height=member_data.get("height"),
                number=member_data.get("number"),
                position=member_data.get("position"),
                owning_org_id=member_data.get("owningOrgId"),
                member_type=member_data.get("memberType"),
                # dont need these, since they wont work due to jwt
                image_url=member_data.get("imageUrl"),
                image2_url=member_data.get("image2Url"),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            members_to_add.append(member)

            # Collect image URLs for later processing
            image_url = member_data.get("imageUrl")
            image2_url = member_data.get("image2Url")
            if image_url or image2_url:
                image_tasks.append((person_id, image_url, image2_url))
        
        
        # Add all new members to the database
        if members_to_add:
            db.add_all(members_to_add)
            
            try:
                db.commit()
                logger.info("Successfully saved team members", extra={
                    "team_id": team_id,
                    "member_count": len(members_to_add)
                })
            except Exception as e:
                db.rollback()
                logger.error("Error saving team members", extra={
                    "team_id": team_id,
                    "error": str(e)
                })
                raise
        else:
            logger.info("No team members to save", extra={"team_id": team_id})


        # Process images asynchronously after saving team members
        if image_tasks:
            asyncio.create_task(self._process_member_images(db, image_tasks))
        
        if not members_to_add:
            logger.info("No team members to save", extra={"team_id": team_id})
    
    async def _process_member_images(self, db: Session, image_tasks: list):
        """Process member images asynchronously"""
        for person_id, image_url, image2_url in image_tasks:
            try:
                await self.person_image_service.save_person_images(db, person_id, image_url, image2_url)
                # Small delay between image downloads to be nice to the server
                await asyncio.sleep(0.2)
            except Exception as e:
                logger.error("Error processing images for person", extra={
                    "person_id": person_id,
                    "error": str(e)
                })