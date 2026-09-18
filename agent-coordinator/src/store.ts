import Database from 'better-sqlite3';
import fs from 'node:fs';
import path from 'node:path';

const dir = path.resolve('data');
fs.mkdirSync(dir, { recursive: true });

export const db = new Database(path.join(dir, 'coordinator.db'));

db.exec(`
CREATE TABLE IF NOT EXISTS agents (
 id INTEGER PRIMARY KEY,
 name TEXT UNIQUE NOT NULL,
 capabilities TEXT NOT NULL,
 last_seen TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS claims (
 path TEXT PRIMARY KEY,
 agent TEXT NOT NULL,
 purpose TEXT NOT NULL,
 expires TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 target TEXT NOT NULL,
 sender TEXT NOT NULL,
 message TEXT NOT NULL,
 created TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decisions (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 topic TEXT NOT NULL,
 decision TEXT NOT NULL,
 rationale TEXT NOT NULL,
 created TEXT NOT NULL
);
`);
