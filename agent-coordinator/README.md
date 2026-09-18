# CryMon Agent Coordinator

This directory contains the design notes for a future machine-assisted coordination service for AI agents.

## Goal

Replace manual coordination documents with a shared state service that agents can query and update.

## Proposed Capabilities

### Agent Registry

Track active agents:

- identity
- capabilities
- current task
- last activity

### File Claims

Prevent collisions:

```text
claim_file(path, agent, purpose)
release_file(path, agent)
```

### Messaging

Allow agents to communicate:

```text
send_message(target, message)
read_messages(agent)
```

### Decisions

Store durable architectural memory:

```text
record_decision(topic, decision, rationale)
```

## Possible Implementation

A lightweight TypeScript service could expose these operations through MCP so coding agents can use them as native tools.

Initial storage options:

- SQLite for local development
- PostgreSQL for shared deployments
- Git-backed event logs for auditability

## Design Principle

The coordinator should not replace Git. Git remains the source of truth for code. The coordinator manages intent, ownership, communication, and project memory.
