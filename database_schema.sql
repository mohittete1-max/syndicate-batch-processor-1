CREATE TABLE match_performance_logs (
    match_id VARCHAR(50) NOT NULL,
    match_name VARCHAR(150) NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    team VARCHAR(50) NOT NULL,
    role VARCHAR(10) NOT NULL,
    credits DECIMAL(4,1) NOT NULL,
    projected_points DECIMAL(5,1) NOT NULL,
    actual_fantasy_points INT DEFAULT 0,
    base_pOWN DECIMAL(5,2) NOT NULL,
    captain_pOWN DECIMAL(5,2) NOT NULL,
    vice_captain_pOWN DECIMAL(5,2) NOT NULL,
    is_selected BOOLEAN DEFAULT FALSE,
    is_captain BOOLEAN DEFAULT FALSE,
    is_vice_captain BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (match_id, player_name)
);
