import Database from 'better-sqlite3';
import { randomUUID } from 'node:crypto';

const db = new Database('coordinator.db');
db.exec(`CREATE TABLE IF NOT EXISTS agents (id TEXT PRIMARY KEY,name TEXT,capabilities TEXT,task TEXT,last_seen TEXT);
CREATE TABLE IF NOT EXISTS claims(path TEXT PRIMARY KEY,owner TEXT,purpose TEXT,expires TEXT);
CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT,sender TEXT,recipient TEXT,message TEXT,created TEXT,read INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS decisions(id INTEGER PRIMARY KEY AUTOINCREMENT,topic TEXT,decision TEXT,rationale TEXT,created TEXT);`);

export const coordinator = {
 register(name:string, capabilities:string[]) {
  const id=randomUUID();
  db.prepare('INSERT INTO agents VALUES(?,?,?,?,?)').run(id,name,JSON.stringify(capabilities),'',new Date().toISOString());
  return {id};
 },
 heartbeat(id:string){db.prepare('UPDATE agents SET last_seen=? WHERE id=?').run(new Date().toISOString(),id)},
 claim(path:string,owner:string,purpose:string){
  const existing=db.prepare('SELECT * FROM claims WHERE path=?').get(path);
  if(existing) return {approved:false,existing};
  db.prepare('INSERT INTO claims VALUES(?,?,?,?)').run(path,owner,purpose,new Date(Date.now()+7200000).toISOString());
  return {approved:true};
 },
 release(path:string,owner:string){db.prepare('DELETE FROM claims WHERE path=? AND owner=?').run(path,owner)},
 message(sender:string,recipient:string,message:string){db.prepare('INSERT INTO messages(sender,recipient,message,created) VALUES(?,?,?,?)').run(sender,recipient,message,new Date().toISOString())},
 decisions(topic:string){return db.prepare('SELECT * FROM decisions WHERE topic LIKE ?').all(`%${topic}%`)}
};

console.log('CryMon Agent Coordinator running');
console.log('Tools: register heartbeat claim release message decisions');
