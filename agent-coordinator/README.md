# CryMon Agent Coordinator

This directory contains the working implementation of the CryMon multi-agent coordination service.

## Purpose

The coordinator manages agent intent, ownership, communication, and architectural memory.
Git remains the source of truth for code.

## Implemented Features

- Agent registration
- Heartbeats
- File ownership claims
- Agent messaging
- Decision storage
- Local SQLite persistence

## Commands

```bash
node src/cli.js register agent-name typescript frontend
node src/cli.js claim src/file.ts agent-name refactor
node src/cli.js message all agent-name "API changed"
node src/cli.js decision auth "Use repository pattern" "Avoid route coupling"
```

## Roadmap

- MCP transport layer
- agent authentication
- remote shared deployment
- stale claim cleanup
- event streaming

## Design Principle

Agents should coordinate through shared state rather than competing edits. The coordinator records intent; Git records implementation.
