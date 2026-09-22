# CryMon Architecture Remediation Plan

## Goal

Reduce world-data drift, improve multi-agent coordination safety, and create the foundation for a procedural FireRed-style regional map.

## Execution Rules

- One focused change per commit.
- Update CURRENT_WORK.md after each completed step.
- Preserve existing map IDs and save compatibility.
- Do not replace source-of-truth files with generated output.

---

## Step 1: Establish World Graph Validation

Create tooling that reads the canonical world layout and verifies:

- every connection references an existing map
- directional links are consistent
- active maps are reachable
- dead-end branches are intentional
- progression does not create impossible locks

Output:

- machine-readable validation report
- developer graph visualization

---

## Step 2: Separate World Data Layers

Clarify responsibilities:

- playable maps: runtime spaces
- world graph: connectivity truth
- Town Map: generated player-facing projection

Do not manually maintain the Town Map image.

---

## Step 3: Procedural Town Map Generator

Generate Sorrow County map from the world graph.

Rules:

- CRYTOWN is the anchor.
- Major destinations become gems.
- Travel areas become path tiles.
- Internal maps collapse into parent destinations.
- Branching relationships remain visible.

Known examples:

- HOME -> CRYTOWN
- Gauntlet floors -> Gauntlet route
- Heavenfall endpoint -> Heavenfall Shrine
- Camp remains a visible destination

---

## Step 4: Schema Validation

Introduce schema checks for content files.

Prevent:

- duplicate IDs
- missing names
- missing connections
- invalid map references

---

## Step 5: Agent Coordination Improvements

Long term:

- keep CURRENT_WORK.md focused on active work
- move historical decisions into DECISIONS.md
- add ownership/claims tracking for files
- avoid simultaneous edits to shared systems

---

## Current Execution Status

Step 1 planning completed.

Next implementation task:
Create world graph validation tooling without changing gameplay data.
