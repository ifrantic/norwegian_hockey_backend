# src/services/claude_service.py
import anthropic
import json
import time
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from src.config.settings import get_settings
from src.utils.database import get_db
from src.utils.logging_config import setup_logging

logger = setup_logging("claude_service")

class ClaudeService:
    def __init__(self):
        self.settings = get_settings()
        if not self.settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        self.cached_schemas = {} 
        self.common_queries = {}

        self.client = anthropic.Anthropic(api_key=self.settings.ANTHROPIC_API_KEY)
        
        # Don't store db connection in __init__, get fresh one for each request
        self.schema_info = self._get_schema_info()
    
    def _get_fresh_db(self):
        """Get a fresh database connection"""
        return next(get_db())
    
    def _get_schema_info(self) -> str:
        """Get comprehensive database schema information for Claude"""
        try:
            db = self._get_fresh_db()
            inspector = inspect(db.bind)
            schema_info = []
            
            # Get all tables and their columns
            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                foreign_keys = inspector.get_foreign_keys(table_name)
                
                table_info = f"\nTable: {table_name}\n"
                table_info += "Columns:\n"
                
                for col in columns:
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    table_info += f"  - {col['name']}: {col['type']} {nullable}\n"
                
                if foreign_keys:
                    table_info += "Foreign Keys:\n"
                    for fk in foreign_keys:
                        table_info += f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}\n"
                
                schema_info.append(table_info)
            
            db.close()
            return "\n".join(schema_info)
        
        except Exception as e:
            logger.error(f"Error getting schema info: {e}")
            return "Schema information unavailable"
    
    async def natural_language_query(self, user_query: str) -> Dict[str, Any]:
        """
        Convert natural language query to SQL and execute it
        """
        start_time = time.time()
        
        # Check cache first
        if user_query in self.common_queries:
            logger.info("Returning cached response")
            return self.common_queries[user_query]
        
        # Get fresh database connection for this request
        db = self._get_fresh_db()
        
        try:
            # Prepare the prompt for Claude
            prompt = f"""
You are a PostgreSQL expert working with a Norwegian hockey database. 

DATABASE SCHEMA:
{self.schema_info}

IMPORTANT CONTEXT:
- This is Norwegian hockey data with teams, tournaments, matches, standings, and players
- Tournament names are in Norwegian (e.g., "Eliteserien", "Postnord-ligaen")
- Team names are Norwegian hockey teams
- team_members table contains players and staff
- Positions might be stored as: goalkeeper, forward, defenseman, coach, etc.
- Check the actual data to see what position values exist

USER QUERY: "{user_query}"

Convert this to a safe PostgreSQL SELECT query. Rules:
1. ONLY return a SELECT statement (no INSERT, UPDATE, DELETE)
2. Use proper JOIN syntax when combining tables
3. Include appropriate WHERE clauses for filtering
4. Use LIMIT to prevent huge result sets (max 50 rows)
5. Handle Norwegian team/tournament names properly
6. For positions, be flexible - try variations like 'goalkeeper', 'goalie', 'gk'
7. Return only the SQL query, no explanations

SQL Query:
"""

            logger.info(f"Sending query to Claude: {user_query}")
            
            # Get SQL from Claude
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            sql_query = response.content[0].text.strip()
            
            # Clean up the SQL (remove any markdown formatting)
            if sql_query.startswith("```sql"):
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            elif sql_query.startswith("```"):
                sql_query = sql_query.replace("```", "").strip()
            
            logger.info(f"Generated SQL: {sql_query}")
            
            # Validate the SQL is a SELECT statement
            if not sql_query.strip().upper().startswith('SELECT'):
                return {
                    "success": False,
                    "query": user_query,
                    "error": "Generated query is not a SELECT statement",
                    "data": []
                }
            
            # Execute the query safely
            result = db.execute(text(sql_query))
            rows = result.fetchall()
            columns = result.keys()
            
            # Convert to list of dictionaries
            data = [dict(zip(columns, row)) for row in rows]
            
            execution_time = time.time() - start_time
            logger.info(f"Query executed in {execution_time:.2f}s, returned {len(data)} rows")
            
            # Cache small, fast queries
            if len(data) < 50 and execution_time < 5:
                self.common_queries[user_query] = {
                    "success": True,
                    "query": user_query,
                    "sql": sql_query,
                    "data": data,
                    "row_count": len(data),
                    "execution_time": execution_time
                }

            return {
                "success": True,
                "query": user_query,
                "sql": sql_query,
                "data": data,
                "row_count": len(data),
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Error in natural language query: {e}")
            # Rollback the transaction if there's an error
            try:
                db.rollback()
            except:
                pass
                
            return {
                "success": False,
                "query": user_query,
                "error": str(e),
                "data": []
            }
        finally:
            # Always close the connection
            try:
                db.close()
            except:
                pass
    
    # ... rest of your methods stay the same but update them to use fresh db connections too
    
    async def get_hockey_insights(self, query_type: str, entity_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get AI-powered insights about hockey data
        """
        try:
            if query_type == "team_analysis" and entity_id:
                return await self._analyze_team(entity_id)
            elif query_type == "tournament_summary" and entity_id:
                return await self._analyze_tournament(entity_id)
            elif query_type == "top_performers":
                return await self._get_top_performers()
            else:
                return {"error": "Invalid query type or missing entity_id"}
                
        except Exception as e:
            logger.error(f"Error getting hockey insights: {e}")
            return {"error": str(e)}
    
# src/services/claude_service.py
async def _analyze_team(self, team_id: int) -> Dict[str, Any]:
    """Analyze a specific team's performance"""
    
    db = self._get_fresh_db()
    try:
        # Get team data - fix the column names
        team_query = text("""
            SELECT t.team_name, t.tournament_id, tr.tournament_name, tr.season_name,
                   s.position, s.matches_played as played, s.points, s.victories as wins, 
                   s.draws, s.losses, s.goals_scored as goals_for, s.goals_conceded as goals_against
            FROM teams t
            LEFT JOIN tournaments tr ON t.tournament_id = tr.tournament_id
            LEFT JOIN standings s ON t.team_id = s.team_id
            WHERE t.team_id = :team_id
        """)
        
        result = db.execute(team_query, {"team_id": team_id})
        team_data = [dict(row._mapping) for row in result.fetchall()]
        
        if not team_data:
            return {"error": "Team not found"}
        
        # Get team members
        members_query = text("""
            SELECT first_name, last_name, position, number, height
            FROM team_members
            WHERE team_id = :team_id
            ORDER BY number
        """)
        
        result = db.execute(members_query, {"team_id": team_id})
        members_data = [dict(row._mapping) for row in result.fetchall()]
        
        # Claude analysis...
        prompt = f"""
Analyze this Norwegian hockey team's performance:

TEAM DATA:
{json.dumps(team_data, indent=2, default=str)}

TEAM MEMBERS:
{json.dumps(members_data, indent=2, default=str)}

Provide a comprehensive analysis including:
1. Team performance summary
2. Strengths and weaknesses based on statistics
3. Key players to watch
4. Tactical insights based on roster composition
5. Comparison with league average (if possible)

Return as JSON with structured insights.
"""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        analysis = response.content[0].text
        
        return {
            "team_id": team_id,
            "team_data": team_data[0] if team_data else {},
            "members_count": len(members_data),
            "ai_analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Error analyzing team: {e}")
        return {"error": str(e)}
    finally:
        db.close()
    
    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'db'):
            self.db.close()