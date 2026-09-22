# World Graph Validation

Purpose: verify that CryMon's region graph remains coherent as maps expand.

The canonical source remains `content/world_map_layout.json`.

Checks:

- referenced maps exist
- active maps are reachable
- collapsed Town Map regions do not orphan playable areas
- connections have valid directions

This is the validation layer before generating Town Map projections.
