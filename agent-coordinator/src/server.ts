import { db } from './store.js';

const now = () => new Date().toISOString();
const parseCapabilities = (value: unknown): string[] => {
  if (Array.isArray(value)) return value.map(String);
  try {
    const parsed = JSON.parse(String(value ?? '[]'));
    return Array.isArray(parsed) ? parsed.map(String) : [];
  } catch {
    return [];
  }
};

function requireAgent(name: string) {
  const agent = db.prepare('SELECT * FROM agents WHERE name = ?').get(name) as any;
  if (!agent) throw new Error(`Unknown agent: ${name}. Register the agent first.`);
  return agent;
}

function removeExpiredClaims() {
  db.prepare('DELETE FROM claims WHERE expires <= ?').run(now());
}

export function registerAgent(name: string, capabilities: string[] = [], task?: string) {
  if (!name?.trim()) throw new Error('Agent name is required');
  const timestamp = now();
  db.prepare(`
    INSERT INTO agents(name, capabilities, task, last_seen, created_at)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(name) DO UPDATE SET
      capabilities = excluded.capabilities,
      task = excluded.task,
      last_seen = excluded.last_seen
  `).run(name.trim(), JSON.stringify(capabilities), task ?? null, timestamp, timestamp);
  const agent = db.prepare('SELECT id, name, capabilities, task, last_seen, created_at FROM agents WHERE name = ?').get(name.trim()) as any;
  return { ...agent, capabilities: parseCapabilities(agent.capabilities) };
}

export function heartbeat(name: string) {
  requireAgent(name);
  const changed = db.prepare('UPDATE agents SET last_seen = ? WHERE name = ?').run(now(), name);
  return { ok: changed.changes === 1, name, last_seen: now() };
}

export function listAgents() {
  return (db.prepare('SELECT id, name, capabilities, task, last_seen, created_at FROM agents ORDER BY name').all() as any[])
    .map(agent => ({ ...agent, capabilities: parseCapabilities(agent.capabilities) }));
}

export function claimFile(file: string, agent: string, purpose: string, minutes = 120) {
  requireAgent(agent);
  if (!file?.trim() || !purpose?.trim()) throw new Error('File path and purpose are required');
  if (!Number.isFinite(minutes) || minutes <= 0 || minutes > 24 * 60) throw new Error('minutes must be between 1 and 1440');
  removeExpiredClaims();
  const existing = db.prepare('SELECT * FROM claims WHERE path = ?').get(file) as any;
  if (existing && existing.agent !== agent) return { approved: false, existing };
  const expires = new Date(Date.now() + minutes * 60000).toISOString();
  db.prepare(`INSERT INTO claims(path, agent, purpose, expires, created_at) VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(path) DO UPDATE SET agent = excluded.agent, purpose = excluded.purpose, expires = excluded.expires`)
    .run(file, agent, purpose, expires, now());
  return { approved: true, path: file, agent, purpose, expires };
}

export function releaseFile(file: string, agent: string) {
  requireAgent(agent);
  const result = db.prepare('DELETE FROM claims WHERE path = ? AND agent = ?').run(file, agent);
  if (result.changes === 0) throw new Error('Claim not found or owned by another agent');
  return { released: true, path: file };
}

export function listClaims() {
  removeExpiredClaims();
  return db.prepare('SELECT * FROM claims ORDER BY path').all();
}

export function sendMessage(sender: string, target: string, message: string, type = 'message') {
  requireAgent(sender);
  if (!target?.trim() || !message?.trim()) throw new Error('Target and message are required');
  const result = db.prepare('INSERT INTO messages(target, sender, type, message, created) VALUES (?, ?, ?, ?, ?)')
    .run(target, sender, type, message, now());
  return db.prepare('SELECT * FROM messages WHERE id = ?').get(result.lastInsertRowid);
}

export function readMessages(target: string, afterId = 0, unreadOnly = false, limit = 50) {
  requireAgent(target);
  const safeLimit = Math.min(Math.max(Number(limit) || 50, 1), 200);
  const unread = unreadOnly ? 'AND acknowledged_at IS NULL' : '';
  return db.prepare(`SELECT * FROM messages WHERE (target = ? OR target = 'all') AND id > ? ${unread} ORDER BY id ASC LIMIT ?`)
    .all(target, Number(afterId) || 0, safeLimit);
}

export function acknowledgeMessage(target: string, id: number) {
  requireAgent(target);
  const result = db.prepare("UPDATE messages SET acknowledged_at = ? WHERE id = ? AND (target = ? OR target = 'all')")
    .run(now(), id, target);
  if (result.changes === 0) throw new Error('Message not found or not addressed to this agent');
  return { acknowledged: true, id };
}

export function recordDecision(topic: string, decision: string, rationale: string, recordedBy?: string) {
  if (recordedBy) requireAgent(recordedBy);
  if (!topic?.trim() || !decision?.trim() || !rationale?.trim()) throw new Error('Topic, decision, and rationale are required');
  const result = db.prepare('INSERT INTO decisions(topic, decision, rationale, created, recorded_by) VALUES (?, ?, ?, ?, ?)')
    .run(topic, decision, rationale, now(), recordedBy ?? null);
  return db.prepare('SELECT * FROM decisions WHERE id = ?').get(result.lastInsertRowid);
}

export function searchDecisions(topic = '') {
  return db.prepare('SELECT * FROM decisions WHERE topic LIKE ? ORDER BY id DESC LIMIT 100').all(`%${topic}%`);
}
