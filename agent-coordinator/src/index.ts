import { acknowledgeMessage, claimFile, heartbeat, listAgents, listClaims, readMessages, recordDecision, registerAgent, releaseFile, searchDecisions, sendMessage } from './server.js';

type Tool = { name: string; description: string; inputSchema: Record<string, unknown>; handler: (args: any) => unknown };
const required = (properties: Record<string, unknown>, names: string[]) => ({ type: 'object', properties, required: names, additionalProperties: false });

export const tools: Tool[] = [
  { name: 'agent.register', description: 'Register or refresh an agent identity.', inputSchema: required({ name: { type: 'string' }, capabilities: { type: 'array', items: { type: 'string' } }, task: { type: 'string' } }, ['name']), handler: a => registerAgent(a.name, a.capabilities ?? [], a.task) },
  { name: 'agent.heartbeat', description: 'Tell the coordinator that an agent is still active.', inputSchema: required({ name: { type: 'string' } }, ['name']), handler: a => heartbeat(a.name) },
  { name: 'agent.list', description: 'List registered agents.', inputSchema: required({}, []), handler: () => listAgents() },
  { name: 'file.claim', description: 'Claim a file for exclusive work.', inputSchema: required({ path: { type: 'string' }, agent: { type: 'string' }, purpose: { type: 'string' }, minutes: { type: 'number' } }, ['path', 'agent', 'purpose']), handler: a => claimFile(a.path, a.agent, a.purpose, a.minutes ?? 120) },
  { name: 'file.release', description: 'Release a file claim owned by the agent.', inputSchema: required({ path: { type: 'string' }, agent: { type: 'string' } }, ['path', 'agent']), handler: a => releaseFile(a.path, a.agent) },
  { name: 'file.list', description: 'List active file claims.', inputSchema: required({}, []), handler: () => listClaims() },
  { name: 'message.send', description: 'Send a message to an agent or to all agents using target "all".', inputSchema: required({ sender: { type: 'string' }, target: { type: 'string' }, message: { type: 'string' }, type: { type: 'string' } }, ['sender', 'target', 'message']), handler: a => sendMessage(a.sender, a.target, a.message, a.type ?? 'message') },
  { name: 'message.read', description: 'Read messages addressed to an agent.', inputSchema: required({ target: { type: 'string' }, afterId: { type: 'number' }, unreadOnly: { type: 'boolean' }, limit: { type: 'number' } }, ['target']), handler: a => readMessages(a.target, a.afterId ?? 0, a.unreadOnly ?? false, a.limit ?? 50) },
  { name: 'message.ack', description: 'Acknowledge a delivered message.', inputSchema: required({ target: { type: 'string' }, id: { type: 'number' } }, ['target', 'id']), handler: a => acknowledgeMessage(a.target, a.id) },
  { name: 'decision.record', description: 'Persist an architectural decision.', inputSchema: required({ topic: { type: 'string' }, decision: { type: 'string' }, rationale: { type: 'string' }, recordedBy: { type: 'string' } }, ['topic', 'decision', 'rationale']), handler: a => recordDecision(a.topic, a.decision, a.rationale, a.recordedBy) },
  { name: 'decision.search', description: 'Search recorded decisions.', inputSchema: required({ topic: { type: 'string' } }, [],), handler: a => searchDecisions(a.topic ?? '') },
];

const send = (value: unknown) => process.stdout.write(`${JSON.stringify(value)}\n`);
const error = (id: unknown, code: number, message: string) => send({ jsonrpc: '2.0', id, error: { code, message } });

async function handle(request: any) {
  if (request.jsonrpc !== '2.0' || typeof request.method !== 'string') return;
  if (request.method === 'notifications/initialized' || request.method === 'notifications/cancelled') return;
  if (request.method === 'initialize') {
    return send({ jsonrpc: '2.0', id: request.id, result: { protocolVersion: request.params?.protocolVersion ?? '2024-11-05', capabilities: { tools: {} }, serverInfo: { name: 'crymon-agent-coordinator', version: '1.0.0' } } });
  }
  if (request.method === 'tools/list') return send({ jsonrpc: '2.0', id: request.id, result: { tools: tools.map(({ name, description, inputSchema }) => ({ name, description, inputSchema })) } });
  if (request.method === 'tools/call') {
    const tool = tools.find(item => item.name === request.params?.name);
    if (!tool) return error(request.id, -32602, `Unknown tool: ${request.params?.name}`);
    try {
      const result = await tool.handler(request.params?.arguments ?? {});
      return send({ jsonrpc: '2.0', id: request.id, result: { content: [{ type: 'text', text: JSON.stringify(result) }], structuredContent: result } });
    } catch (cause) {
      return send({ jsonrpc: '2.0', id: request.id, result: { isError: true, content: [{ type: 'text', text: cause instanceof Error ? cause.message : String(cause) }] } });
    }
  }
  return error(request.id, -32601, `Method not found: ${request.method}`);
}

let buffer = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => {
  buffer += chunk;
  const lines = buffer.split('\n');
  buffer = lines.pop() ?? '';
  for (const line of lines) {
    if (!line.trim()) continue;
    try { void handle(JSON.parse(line)); } catch (cause) { error(null, -32700, cause instanceof Error ? cause.message : String(cause)); }
  }
});
process.stderr.write('CryMon Agent Coordinator MCP server ready\n');
