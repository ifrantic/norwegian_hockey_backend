import httpx
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from src.config.settings import Settings
from src.models.organisation import Organisation
from src.utils.logging_config import setup_logging

# Set up logging
logger = setup_logging("organisation_service")

class OrganisationService:
    def __init__(self):
        self.settings = Settings()
        self.base_url = self.settings.API_BASE_URL
    
    async def fetch_organisations(self, org_ids: List[int], max_retries: int = 3) -> Dict[str, Any]:
        """
        Fetch organisation data for a list of organization IDs.
        The API expects repeated orgIds parameters like:
        /org/Organisation?orgIds=21561&orgIds=22629
        """
        if not org_ids:
            raise ValueError("No organisation IDs provided")
            
        retries = 0
        logger.info("Fetching organisations", extra={
            "org_count": len(org_ids),
            "retry_count": retries,
            "max_retries": max_retries
        })
        
        # Build URL with repeated orgIds parameters
        base_url = f"{self.base_url}/org/Organisation"
        params = []
        for org_id in org_ids:
            params.append(f"orgIds={org_id}")
        
        url = f"{base_url}?{'&'.join(params)}"
        
        while retries < max_retries:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    logger.info(f"Calling URL: {url}", extra={"org_count": len(org_ids)})
                    response = await client.get(url)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Make sure we got a list back
                    if not isinstance(data, list):
                        data = [data] if data else []
                        
                    logger.info("Successfully fetched organisations", extra={
                        "org_count": len(data)
                    })
                    return {"organisations": data}
            
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                retries += 1
                logger.warning("API request failed, retrying", extra={
                    "url": url[:100] + "..." if len(url) > 100 else url,
                    "retry_count": retries,
                    "max_retries": max_retries,
                    "error": str(e),
                    "wait_seconds": 2 ** retries
                })
                
                if retries == max_retries:
                    logger.error("Failed to fetch organisations after maximum retries", extra={
                        "org_count": len(org_ids),
                        "retry_count": retries,
                        "error": str(e)
                    })
                    raise Exception(f"Failed to fetch organisations after {max_retries} attempts: {str(e)}")
                    
                await asyncio.sleep(2 ** retries)  # Exponential backoff
    
    def save_organisations(self, db: Session, data: Dict[str, Any]) -> None:
        """Save organisation data to the database"""
        organisations_to_add = []
        count_new = 0
        count_updated = 0
        
        for org_data in data.get("organisations", []):
            org_id = org_data.get("orgId")
            if not org_id:
                logger.warning("Organisation data missing orgId", extra={
                    "org_data": str(org_data)[:100] + "..."
                })
                continue
                
            # Check if organisation already exists
            existing_org = db.query(Organisation).filter(
                Organisation.org_id == org_id
            ).first()
            
            if existing_org:
                # Update existing organisation
                existing_org.reference_id = org_data.get("referenceId")
                existing_org.org_name = org_data.get("orgName")
                existing_org.abbreviation = org_data.get("abbreviation")
                existing_org.describing_name = org_data.get("describingName")
                existing_org.org_type_id = org_data.get("orgTypeId")
                existing_org.organisation_number = org_data.get("organisationNumber")
                existing_org.email = org_data.get("email")
                existing_org.home_page = org_data.get("homePage")
                existing_org.mobile_phone = org_data.get("mobilePhone")
                existing_org.address_line1 = org_data.get("addressLine1")
                existing_org.address_line2 = org_data.get("addressLine2")
                existing_org.city = org_data.get("city")
                existing_org.country = org_data.get("country")
                existing_org.country_id = org_data.get("countryId")
                existing_org.post_code = org_data.get("postCode")
                existing_org.longitude = org_data.get("longitude")
                existing_org.latitude = org_data.get("latitude")
                
                # Only update logo if not NULL to avoid storing large strings repeatedly
                if org_data.get("orgLogoBase64"):
                    existing_org.org_logo_base64 = org_data.get("orgLogoBase64")
                
                existing_org.members = org_data.get("members")
                existing_org.updated_at = datetime.now()
                count_updated += 1
            else:
                # Create new organisation
                new_org = Organisation(
                    org_id=org_id,
                    reference_id=org_data.get("referenceId"),
                    org_name=org_data.get("orgName"),
                    abbreviation=org_data.get("abbreviation"),
                    describing_name=org_data.get("describingName"),
                    org_type_id=org_data.get("orgTypeId"),
                    organisation_number=org_data.get("organisationNumber"),
                    email=org_data.get("email"),
                    home_page=org_data.get("homePage"),
                    mobile_phone=org_data.get("mobilePhone"),
                    address_line1=org_data.get("addressLine1"),
                    address_line2=org_data.get("addressLine2"),
                    city=org_data.get("city"),
                    country=org_data.get("country"),
                    country_id=org_data.get("countryId"),
                    post_code=org_data.get("postCode"),
                    longitude=org_data.get("longitude"),
                    latitude=org_data.get("latitude"),
                    org_logo_base64=org_data.get("orgLogoBase64"),
                    members=org_data.get("members"),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                organisations_to_add.append(new_org)
                count_new += 1
        
        # Add all new organisations to the database
        if organisations_to_add:
            db.add_all(organisations_to_add)
            
        # Commit changes
        try:
            db.commit()
            logger.info("Successfully saved organisations", extra={
                "new_count": count_new,
                "updated_count": count_updated
            })
        except Exception as e:
            db.rollback()
            logger.error("Error saving organisations", extra={
                "error": str(e)
            })
            raise