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

-- Create matches table
CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY,
    tournament_id INTEGER NOT NULL REFERENCES tournaments(tournament_id),
    match_no VARCHAR(50),
    activity_area_id INTEGER,
    activity_area_latitude FLOAT,
    activity_area_longitude FLOAT,
    activity_area_name VARCHAR(255),
    activity_area_no VARCHAR(50),
    adm_org_id INTEGER,
    arr_org_id INTEGER,
    arr_org_no VARCHAR(50),
    arr_org_name VARCHAR(255),
    awayteam_id INTEGER,
    awayteam_org_no VARCHAR(50),
    awayteam VARCHAR(255),
    awayteam_org_name VARCHAR(255),
    awayteam_overridden_name VARCHAR(255),
    awayteam_club_org_id INTEGER,
    hometeam_id INTEGER,
    hometeam VARCHAR(255),
    hometeam_org_name VARCHAR(255),
    hometeam_overridden_name VARCHAR(255),
    hometeam_org_no VARCHAR(50),
    hometeam_club_org_id INTEGER,
    round_id INTEGER,
    round_name VARCHAR(100),
    season_id INTEGER,
    tournament_name VARCHAR(255),
    match_date TIMESTAMP,
    match_start_time INTEGER,
    match_end_time INTEGER,
    venue_unit_id INTEGER,
    venue_unit_no VARCHAR(50),
    venue_id INTEGER,
    venue_no VARCHAR(50),
    physical_area_id INTEGER,
    home_goals INTEGER,
    away_goals INTEGER,
    match_end_result VARCHAR(50),
    live_arena BOOLEAN,
    live_client_type VARCHAR(100),
    status_type_id INTEGER,
    status_type VARCHAR(100),
    last_change_date TIMESTAMP,
    spectators INTEGER,
    actual_match_date TIMESTAMP,
    actual_match_start_time INTEGER,
    actual_match_end_time INTEGER,
    sport_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Create standings table
-- Create standings table with all the detailed fields
CREATE TABLE IF NOT EXISTS standings (
    id SERIAL PRIMARY KEY,
    tournament_id INTEGER NOT NULL REFERENCES tournaments(tournament_id),
    team_id INTEGER NOT NULL,
    team_name VARCHAR(255),
    overridden_name VARCHAR(255),
    position INTEGER,
    entry_id INTEGER,
    
    -- Match stats
    matches_played INTEGER,
    matches_home INTEGER,
    matches_away INTEGER,
    
    -- Points
    points INTEGER,
    points_home INTEGER,
    points_away INTEGER,
    points_start INTEGER,
    total_points INTEGER,
    
    -- Victories
    victories INTEGER,
    victories_home INTEGER,
    victories_away INTEGER,
    victories_fulltime_total INTEGER,
    victories_fulltime_home INTEGER,
    victories_fulltime_away INTEGER,
    victories_overtime_total INTEGER,
    victories_overtime_home INTEGER,
    victories_overtime_away INTEGER,
    victories_penalties_total INTEGER,
    victories_penalties_home INTEGER,
    victories_penalties_away INTEGER,
    
    -- Draws
    draws INTEGER,
    draws_home INTEGER,
    draws_away INTEGER,
    
    -- Losses
    losses INTEGER,
    losses_home INTEGER,
    losses_away INTEGER,
    losses_fulltime_total INTEGER,
    losses_fulltime_home INTEGER,
    losses_fulltime_away INTEGER,
    losses_overtime_total INTEGER,
    losses_overtime_home INTEGER,
    losses_overtime_away INTEGER,
    losses_penalties_total INTEGER,
    losses_penalties_home INTEGER,
    losses_penalties_away INTEGER,
    
    -- Goals
    goals_scored INTEGER,
    goals_scored_home INTEGER,
    goals_scored_away INTEGER,
    goals_conceded INTEGER,
    goals_conceded_home INTEGER,
    goals_conceded_away INTEGER,
    goals_diff INTEGER,
    goals_ratio FLOAT,
    
    -- Penalty minutes
    penalty_minutes INTEGER,
    
    -- Record strings
    home_record VARCHAR(50),
    away_record VARCHAR(50),
    
    -- Formatted strings
    goals_home_formatted VARCHAR(50),
    goals_away_formatted VARCHAR(50),
    total_goals_formatted VARCHAR(50),
    
    -- Additional fields
    team_penalty VARCHAR(255),
    team_penalty_negative INTEGER,
    team_penalty_positive INTEGER,
    dispensation BOOLEAN,
    team_entry_status VARCHAR(50),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraint to ensure a team only appears once per tournament
    UNIQUE(tournament_id, team_id)
);

-- Add indexes for standings queries
CREATE INDEX idx_standings_tournament_id ON standings(tournament_id);
CREATE INDEX idx_standings_team_id ON standings(team_id);
CREATE INDEX idx_standings_position ON standings(position);


-- Add indexes for match queries
CREATE INDEX idx_matches_tournament_id ON matches(tournament_id);
CREATE INDEX idx_matches_match_date ON matches(match_date);
CREATE INDEX idx_matches_hometeam_id ON matches(hometeam_id);
CREATE INDEX idx_matches_awayteam_id ON matches(awayteam_id);


-- Create organisations table
CREATE TABLE IF NOT EXISTS organisations (
    org_id INTEGER PRIMARY KEY,
    reference_id VARCHAR(255),
    org_name VARCHAR(255),
    abbreviation VARCHAR(255),
    describing_name VARCHAR(255),
    org_type_id INTEGER,
    organisation_number VARCHAR(50),
    email VARCHAR(255),
    home_page VARCHAR(255),
    mobile_phone VARCHAR(50),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    country VARCHAR(100),
    country_id VARCHAR(50),
    post_code VARCHAR(20),
    longitude FLOAT,
    latitude FLOAT,
    org_logo_base64 TEXT,
    members INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for organisation queries
CREATE INDEX idx_organisations_name ON organisations(org_name);
CREATE INDEX idx_organisations_city ON organisations(city);


---------------------------------------
--------------------------------------
-- Create a read-only schema for views
-- only after the tables are created
CREATE SCHEMA IF NOT EXISTS readonly;


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


-- Grant usage on the schema but not create permissions
-- Do this after the tables are created, and after the view is created
GRANT USAGE ON SCHEMA readonly TO PUBLIC;
REVOKE CREATE ON SCHEMA readonly FROM PUBLIC;
GRANT SELECT ON readonly.team_tournament_classes TO PUBLIC;
REVOKE INSERT, UPDATE, DELETE ON readonly.team_tournament_classes FROM PUBLIC;