-- Create tournaments table
CREATE TABLE IF NOT EXISTS tournaments (
    tournament_id INTEGER PRIMARY KEY,
    season_id INTEGER NOT NULL,
    tournament_no VARCHAR(50),
    from_date TIMESTAMP,
    to_date TIMESTAMP,
    is_archival BOOLEAN,
    is_deleted BOOLEAN,
    org_id_owner INTEGER,
    parent_tournament_id INTEGER,
    season_name VARCHAR(100),
    tournament_name VARCHAR(255),
    tournament_short_name VARCHAR(100),
    division INTEGER,
    logo_url VARCHAR(255),
    is_table_published BOOLEAN,
    is_result_published BOOLEAN,
    are_matches_published BOOLEAN,
    publish_matches_to_date TIMESTAMP,
    are_referees_published BOOLEAN,
    publish_referees_to_date TIMESTAMP,
    are_statistics_published BOOLEAN,
    are_teams_published BOOLEAN,
    live_arena BOOLEAN,
    live_client BOOLEAN,
    withdrawals_visible BOOLEAN,
    team_entry BOOLEAN,
    tournament_type VARCHAR(50),
    sport_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tournament classes table
CREATE TABLE IF NOT EXISTS tournament_classes (
    id SERIAL PRIMARY KEY,
    tournament_id INTEGER NOT NULL REFERENCES tournaments(tournament_id),
    class_id INTEGER NOT NULL,
    class_name VARCHAR(100),
    from_age INTEGER,
    to_age INTEGER,
    allowed_from_age INTEGER,
    allowed_to_age INTEGER,
    gender VARCHAR(20),
    live_arena_storage VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tournament_id, class_id)
);

-- Add indexes
CREATE INDEX idx_tournaments_season_id ON tournaments(season_id);
CREATE INDEX idx_tournament_classes_tournament_id ON tournament_classes(tournament_id);