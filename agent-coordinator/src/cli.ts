#!/usr/bin/env node
import { acknowledgeMessage, claimFile, heartbeat, listAgents, listClaims, readMessages, recordDecision, registerAgent, releaseFile, searchDecisions, sendMessage } from './server.js';

const [command, ...args] = process.argv.slice(2);
const output = (value: unknown) => console.log(JSON.stringify(value ?? { ok: true }));

try {
  switch (command) {
    case 'register': output(registerAgent(args[0], args.slice(1))); break;
    case 'heartbeat': output(heartbeat(args[0])); break;
    case 'agents': output(listAgents()); break;
    case 'claims': output(listClaims()); break;
    case 'claim': output(claimFile(args[0], args[1], args.slice(2).join(' '))); break;
    case 'release': output(releaseFile(args[0], args[1])); break;
    case 'message': output(sendMessage(args[0], args[1], args.slice(2).join(' '))); break;
    case 'messages': output(readMessages(args[0], Number(args[1] ?? 0), args[2] === 'unread')); break;
    case 'ack': output(acknowledgeMessage(args[0], Number(args[1]))); break;
    case 'decision': output(recordDecision(args[0], args[1], args.slice(2).join(' '), process.env.AGENT)); break;
    case 'decisions': output(searchDecisions(args[0] ?? '')); break;
    default:
      console.error('Commands: register heartbeat agents claims claim release message messages ack decision decisions');
      process.exitCode = 1;
  }
} catch (error) {
  console.error(JSON.stringify({ error: error instanceof Error ? error.message : String(error) }));
  process.exitCode = 1;
}
