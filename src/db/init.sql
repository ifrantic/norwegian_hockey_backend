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

-- create table for tournament teams with composite primary key
CREATE TABLE IF NOT EXISTS teams (
    team_id INTEGER NOT NULL,
    tournament_id INTEGER NOT NULL REFERENCES tournaments(tournament_id),
    club_org_id INTEGER,
    team_no INTEGER,
    team_name VARCHAR(100),
    overridden_name VARCHAR(100),
    describing_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (team_id, tournament_id)
);

CREATE INDEX idx_teams_tournament_id ON teams(tournament_id);
CREATE INDEX idx_teams_team_id ON teams(team_id);


----------------------
-- Create a read-only schema for views
CREATE SCHEMA IF NOT EXISTS readonly;

-- Grant usage on the schema but not create permissions
GRANT USAGE ON SCHEMA readonly TO PUBLIC;
REVOKE CREATE ON SCHEMA readonly FROM PUBLIC;
GRANT SELECT ON readonly.team_tournament_classes TO PUBLIC;
REVOKE INSERT, UPDATE, DELETE ON readonly.team_tournament_classes FROM PUBLIC;


-- Create the team_tournament_classes view in the readonly schema
CREATE OR REPLACE VIEW readonly.team_tournament_classes AS
SELECT 
    t.team_id,
    t.team_name,
    t.describing_name,
    t.club_org_id,
    t.team_no,
    t.overridden_name,
    tr.tournament_id,
    tr.tournament_name,
    tr.tournament_short_name,
    tr.season_id,
    tr.season_name,
    tr.from_date,
    tr.to_date,
    tr.division,
    tr.tournament_type,
    tc.class_id,
    tc.class_name,
    tc.gender,
    tc.from_age,
    tc.to_age,
    tc.allowed_from_age,
    tc.allowed_to_age
FROM 
    teams t
JOIN 
    tournaments tr ON t.tournament_id = tr.tournament_id
LEFT JOIN
    tournament_classes tc ON tr.tournament_id = tc.tournament_id;


-- Create useful indexes to improve view performance
CREATE INDEX IF NOT EXISTS idx_teams_describing_name ON teams(describing_name);
CREATE INDEX IF NOT EXISTS idx_tournament_classes_gender ON tournament_classes(gender);
CREATE INDEX IF NOT EXISTS idx_tournament_classes_from_age ON tournament_classes(from_age);
CREATE INDEX IF NOT EXISTS idx_tournament_classes_to_age ON tournament_classes(to_age);