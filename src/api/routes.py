from flask import Flask, jsonify, request
from src.utils.database import get_db
from src.services.team_service import TeamService
from src.models.tournament import Tournament
from src.models.team import Team

# TODO: This is just an example of how to proceed with the API
app = Flask(__name__)
team_service = TeamService()

@app.route('/api/teams/<int:team_id>/tournaments', methods=['GET'])
def get_team_tournaments(team_id):
    db = next(get_db())
    try:
        # Use existing service logic
        query = db.query(
            Team.team_id, 
            Team.team_name,
            Tournament.tournament_name,
            Tournament.season_name
        ).join(
            Tournament, Team.tournament_id == Tournament.tournament_id
        ).filter(
            Team.team_id == team_id
        ).all()
        
        # Format response as JSON
        result = [
            {
                'team_id': r[0],
                'team_name': r[1], 
                'tournament_name': r[2],
                'season_name': r[3]
            } 
            for r in query
        ]
        return jsonify(result)
    finally:
        db.close()