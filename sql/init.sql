-- processed_messages (existing, kept for compatibility)
CREATE TABLE IF NOT EXISTS processed_messages (
    channel    TEXT    NOT NULL,
    message_id INTEGER NOT NULL,
    timestamp  TEXT    NOT NULL,
    score      INTEGER,
    PRIMARY KEY (channel, message_id)
);

-- dialogue history for chat automation
CREATE TABLE IF NOT EXISTS dialogue_history (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    role       TEXT    NOT NULL CHECK(role IN ('user', 'assistant')),
    content    TEXT    NOT NULL,
    created_at TEXT    DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_dialogue_user ON dialogue_history(user_id);

-- channel profiles from streaming profiler
CREATE TABLE IF NOT EXISTS channel_profiles (
    channel_name TEXT PRIMARY KEY,
    profile_json TEXT,
    updated_at   TEXT DEFAULT (datetime('now'))
);

-- hot guest leads from guest mode
CREATE TABLE IF NOT EXISTS guest_leads (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    username       TEXT,
    source_channel TEXT,
    segment        TEXT    DEFAULT 'other',
    activity_score INTEGER DEFAULT 3,
    is_hot         INTEGER DEFAULT 1,
    raw_text       TEXT,
    created_at     TEXT    DEFAULT (datetime('now'))
);
