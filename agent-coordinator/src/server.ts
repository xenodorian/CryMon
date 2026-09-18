import { db } from './store.js';

const now = () => new Date().toISOString();

export function registerAgent(name: string, capabilities: string[]) {
  db.prepare(`INSERT INTO agents(name, capabilities, last_seen)
    VALUES(?,?,?)
    ON CONFLICT(name) DO UPDATE SET capabilities=?, last_seen=?`)
    .run(name, JSON.stringify(capabilities), now(), JSON.stringify(capabilities), now());
}

export function heartbeat(name: string) {
  db.prepare('UPDATE agents SET last_seen=? WHERE name=?').run(now(), name);
}

export function claimFile(file: string, agent: string, purpose: string, minutes = 120) {
  const expires = new Date(Date.now() + minutes * 60000).toISOString();
  const existing = db.prepare('SELECT * FROM claims WHERE path=?').get(file) as any;
  if (existing && new Date(existing.expires) > new Date()) return { approved: false, owner: existing.agent };
  db.prepare(`INSERT OR REPLACE INTO claims(path,agent,purpose,expires) VALUES(?,?,?,?)`)
    .run(file, agent, purpose, expires);
  return { approved: true, expires };
}

export function releaseFile(file: string, agent: string) {
  db.prepare('DELETE FROM claims WHERE path=? AND agent=?').run(file, agent);
}

export function sendMessage(sender: string, target: string, message: string) {
  db.prepare('INSERT INTO messages(target,sender,message,created) VALUES(?,?,?,?)')
    .run(target, sender, message, now());
}

export function readMessages(target: string) {
  return db.prepare('SELECT * FROM messages WHERE target=? OR target=? ORDER BY id DESC')
    .all(target, 'all');
}

export function recordDecision(topic: string, decision: string, rationale: string) {
  db.prepare('INSERT INTO decisions(topic,decision,rationale,created) VALUES(?,?,?,?)')
    .run(topic, decision, rationale, now());
}

export function searchDecisions(topic: string) {
  return db.prepare('SELECT * FROM decisions WHERE topic LIKE ?').all(`%${topic}%`);
}
