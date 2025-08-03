# Python Backend Project
## Thoughts
Ok, so how should I start? I need a backend postgres database, service that gets data from many api endpoints and updates the data, and then begin to work with the joins and views etc, and then create an api that returns data from the backend database. I think. I want to use python for the backend. Also, in initial testphase, the postgresql database will be a docker container having a persistent storage on my laptop. When in production ( in the end ), the backend will be on a virtual linux server I rent, running in docker or k8s. It will be containerized.

## Overview
This project is a Python backend application that interfaces with a PostgreSQL database. It fetches data from multiple API endpoints, updates the database, and provides an API for data retrieval.

## Features
- PostgreSQL database connection
- Data fetching from multiple APIs
- Data updates and handling
- API endpoints for data access
- Docker containerization for development and production
- Data is stored at C:\Users\[username]\AppData\Local\Docker\wsl\data\ext4.vhdx

## Getting Started

### Prerequisites
- Python 3.x
- Docker and Docker Compose

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd python-backend
   ```

2. Install the required packages:
   ```bash
   pip -m venv venv
   pip install -r requirements.txt
   ```

3. Set up the environment variables:
   - Copy `.env.example` to `.env` and fill in the necessary details.

### Running the Application
1. Build the Docker containers:
   ```bash
   docker-compose up --build
   ```

2. Access the API at `http://localhost:<port>`.

## Testing
To run the tests, use:
```bash
pytest tests/
```

## update database with test scripts
- python -m src.scripts.fetch_tournaments
- python -m src.scripts.fetch_teams
- python -m src.scripts.fetch_matches
- python -m src.scripts.fetch_organisations
- python -m src.scripts.fetch_standings
- python -m src.scripts.fetch_team_members



## License
This project is licensed under the MIT License. See the LICENSE file for details.


## TODO

- setup minio for storage of images. It is working, but not robust.

- next endpoints to get data from:
- tournamentsInSeason [ok](https://sf34-terminlister-prod-app.azurewebsites.net/ta/Tournament/Season/201036)
- TournamentTeams [ok](https://sf34-terminlister-prod-app.azurewebsites.net/ta/TournamentTeams/?tournamentId={{tournamentId}})
- TournamentMatches [ok](https://sf34-terminlister-prod-app.azurewebsites.net/ta/TournamentMatches/?tournamentId={{tournamentId}})
- TournamentStandings [ok](https://sf34-terminlister-prod-app.azurewebsites.net/ta/TournamentStandings/?tournamentId={{tournamentId}})
- TeamMembers [ok](https://sf34-terminlister-prod-app.azurewebsites.net/ta/TeamMembers/{{teamId}})
- Organisation [ok](https://sf34-terminlister-prod-app.azurewebsites.net/org/Organisation?orgIds={{orgId}})

- create db views and api routes