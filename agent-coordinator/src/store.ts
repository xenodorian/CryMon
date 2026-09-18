import Database from 'better-sqlite3';
import fs from 'node:fs';
import path from 'node:path';

const dataDir = path.resolve('data');
fs.mkdirSync(dataDir, { recursive: true });

export const db = new Database(path.join(dataDir, 'coordinator.db'));
db.pragma('journal_mode = WAL');
db.pragma('busy_timeout = 5000');

db.exec(`
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
  CREATE INDEX IF NOT EXISTS messages_target_id ON messages(target, id);
  CREATE INDEX IF NOT EXISTS claims_expires ON claims(expires);
  CREATE INDEX IF NOT EXISTS decisions_topic ON decisions(topic);
`);

export function closeStore() {
  if (db.open) db.close();
}
