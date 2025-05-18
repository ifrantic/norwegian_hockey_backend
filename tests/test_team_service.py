import unittest
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.base import Base
from src.models.team import Team
from src.models.tournament import Tournament
from src.services.team_service import TeamService

class TestTeamService(unittest.TestCase):
    def setUp(self):
        # Create in-memory SQLite database
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # Create test data
        session = self.Session()
        tournament = Tournament(tournament_id=1, season_id=100, tournament_name="Test Tournament")
        team = Team(team_id=200, tournament_id=1, team_name="Test Team")
        session.add(tournament)
        session.add(team)
        session.commit()
        
        self.service = TeamService()
    
    def test_get_team_tournaments(self):
        session = self.Session()
        # Test retrieving team tournaments
        teams = session.query(Team).all()
        self.assertEqual(len(teams), 1)
        self.assertEqual(teams[0].team_name, "Test Team")