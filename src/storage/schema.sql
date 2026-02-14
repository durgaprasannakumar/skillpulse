CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    title TEXT,
    company TEXT,
    location TEXT,
    description TEXT,
    created TEXT,
    fetched_at TEXT
);

CREATE TABLE IF NOT EXISTS skills_daily (
    date TEXT,
    skill TEXT,
    count INTEGER
);
