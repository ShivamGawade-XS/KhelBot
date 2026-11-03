-- ==============================================================
-- KhelBot Production Database Schema (Supabase PostgreSQL)
-- ==============================================================

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username TEXT,
    favorite_team TEXT,
    query_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for Telegram ID lookups
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);

-- 2. Reminders Table
CREATE TABLE IF NOT EXISTS reminders (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    team_name TEXT NOT NULL,
    match_id TEXT,
    remind_at TIMESTAMPTZ NOT NULL,
    sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for pending reminder queries
CREATE INDEX IF NOT EXISTS idx_reminders_pending ON reminders(sent, remind_at);

-- 3. Predictions Table
CREATE TABLE IF NOT EXISTS predictions (
    id BIGSERIAL PRIMARY KEY,
    match_id TEXT NOT NULL,
    match_name TEXT NOT NULL,
    predicted_winner TEXT NOT NULL,
    confidence_pct REAL NOT NULL,
    actual_winner TEXT,
    is_correct BOOLEAN,
    match_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for match verification lookups
CREATE INDEX IF NOT EXISTS idx_predictions_match_id ON predictions(match_id);

-- 4. Stored Procedures & Functions
CREATE OR REPLACE FUNCTION increment_query_count(uid BIGINT)
RETURNS VOID AS $$
BEGIN
    INSERT INTO users (telegram_id, query_count)
    VALUES (uid, 1)
    ON CONFLICT (telegram_id)
    DO UPDATE SET query_count = users.query_count + 1, updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_prediction_accuracy()
RETURNS TABLE (total BIGINT, correct BIGINT, accuracy REAL) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total,
        COUNT(*) FILTER (WHERE is_correct = TRUE)::BIGINT as correct,
        COALESCE(
            ROUND((COUNT(*) FILTER (WHERE is_correct = TRUE)::DECIMAL / NULLIF(COUNT(*), 0) * 100.0)::NUMERIC, 1)::REAL,
            0.0::REAL
        ) as accuracy
    FROM predictions
    WHERE actual_winner IS NOT NULL;
END;
$$ LANGUAGE plpgsql;

