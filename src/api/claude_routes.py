# src/api/claude_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from src.services.claude_service import ClaudeService
from src.utils.logging_config import setup_logging

logger = setup_logging("claude_api")

# Create router instead of app
router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class InsightRequest(BaseModel):
    query_type: str
    entity_id: Optional[int] = None

@router.get("/")
async def root():
    return {
        "message": "Norwegian Hockey AI API",
        "version": "1.0.0",
        "endpoints": {
            "natural_query": "/api/query",
            "insights": "/api/insights",
            "health": "/health"
        }
    }

@router.post("/api/query")
async def natural_language_query(request: QueryRequest):
    """
    Ask questions about hockey data in natural language
    
    Examples:
    - "Show me all teams from Oslo"
    - "Which team scored the most goals this season?"
    - "List players over 25 years old"
    - "Top 5 teams in Eliteserien standings"
    """
    try:
        claude_service = ClaudeService()
        result = await claude_service.natural_language_query(request.query)
        return result
    except Exception as e:
        logger.error(f"Error in natural language query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/insights")
async def get_insights(request: InsightRequest):
    """
    Get AI-powered insights about teams, tournaments, or players
    
    Query types:
    - team_analysis: Analyze a specific team (requires entity_id = team_id)
    - tournament_summary: Summarize a tournament (requires entity_id = tournament_id)
    - top_performers: Get top performing players/teams
    """
    try:
        claude_service = ClaudeService()
        result = await claude_service.get_hockey_insights(
            request.query_type, 
            request.entity_id
        )
        return result
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Norwegian Hockey AI API"
    }

@router.get("/api/examples")
async def get_examples():
    """Get example queries to help users get started"""
    return {
        "natural_language_examples": [
            "Show me all teams from Bergen",
            "Which team has the most wins this season?",
            "List goalkeepers in Eliteserien",
            "Top 5 teams by points",
            "Show me matches played in December 2024",
            "Which players are over 30 years old?",
            "Teams with more than 20 goals scored"
        ],
        "insights_examples": [
            {
                "type": "team_analysis",
                "description": "Analyze team performance",
                "example": {"query_type": "team_analysis", "entity_id": 12345}
            },
            {
                "type": "tournament_summary", 
                "description": "Tournament overview",
                "example": {"query_type": "tournament_summary", "entity_id": 429552}
            },
            {
                "type": "top_performers",
                "description": "Find top performers",
                "example": {"query_type": "top_performers"}
            }
        ]
    }