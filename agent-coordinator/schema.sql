CREATE TABLE IF NOT EXISTS agents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  capabilities TEXT NOT NULL DEFAULT '[]',
  task TEXT,
  last_seen TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS claims (
  path TEXT PRIMARY KEY,
  agent TEXT NOT NULL,
  purpose TEXT NOT NULL,
  expires TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (agent) REFERENCES agents(name)
);

CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  target TEXT NOT NULL,
  sender TEXT NOT NULL,
  type TEXT NOT NULL DEFAULT 'message',
  message TEXT NOT NULL,
  created TEXT NOT NULL,
  acknowledged_at TEXT
);

CREATE TABLE IF NOT EXISTS decisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  topic TEXT NOT NULL,
  decision TEXT NOT NULL,
  rationale TEXT NOT NULL,
  created TEXT NOT NULL,
  recorded_by TEXT
);
