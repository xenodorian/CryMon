# CryMon Agent Coordinator

A local MCP stdio server that lets coding agents share coordination state without competing blindly over the same work.

## Start the MCP server

From this directory:

```bash
npm install
npm start
```

The process speaks newline-delimited JSON-RPC 2.0 on **stdout**. Logs go to stderr so the stream remains MCP-safe. Configure the MCP client to launch `npm start` with this directory as its working directory.

Implemented MCP tools:

- `agent.register`, `agent.heartbeat`, `agent.list`
- `file.claim`, `file.release`, `file.list`
- `message.send`, `message.read`, `message.ack`
- `decision.record`, `decision.search`

Agents must register before sending messages, claiming files, or reading messages. Messages can target one agent or `all`. Claims expire automatically when they are checked after their expiration time.

## CLI

The same service layer is available for local inspection:

```bash
npm run cli -- register agent-name typescript frontend
npm run cli -- message agent-name all "API changed"
npm run cli -- messages agent-name
```

State is stored in `data/coordinator.db` using SQLite. Git remains the source of truth for code; this service records intent, messages, and decisions.
