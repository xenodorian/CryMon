# CryMon AI Agent Coordination Protocol

## Purpose

This document defines how AI agents collaborate while modifying CryMon.

`AGENTS.md` contains environment/runtime rules. This document contains project collaboration rules.

## Before Editing

Every agent should:

1. Read `README.md`.
2. Read `AGENTS.md`.
3. Read `CURRENT_WORK.md`.
4. Check recent commits and active pull requests.
5. Identify files or systems that may overlap with existing work.

## Work Ownership

Before making substantial changes, an agent should claim ownership in the coordination system.

A claim should include:

- Agent identity
- Goal
- Files or modules affected
- Expected completion point
- Dependencies or risks

Agents should avoid modifying files actively owned by another agent unless coordinating directly.

## Communication Model

Agents should communicate through structured events rather than relying only on commit history.

Recommended events:

- `CLAIM`: agent starts work on an area
- `UPDATE`: progress or architectural changes
- `BLOCKED`: needs input or another agent's work
- `RELEASE`: work area is available
- `DECISION`: records an important design choice

## Shared Decisions

Important architectural choices should be recorded permanently.

Examples:

- database patterns
- API contracts
- authentication decisions
- folder conventions
- major dependency choices

## Conflict Resolution

When agents overlap:

1. Prefer communication over competing edits.
2. Preserve working behavior.
3. Prefer smaller, reversible commits.
4. Record why a decision was made.

## Future Coordination Service

CryMon may provide a machine-readable coordination service with tools such as:

- `register_agent`
- `claim_file`
- `release_file`
- `send_message`
- `record_decision`
- `request_review`

Until then, `CURRENT_WORK.md` acts as the shared coordination state.

## Agent Completion Checklist

Before finishing:

- Update coordination state.
- Summarize changed files.
- Document important decisions.
- Run applicable validation.
- Release owned resources.
