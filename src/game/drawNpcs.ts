/** Pack NPC overworld draw. Wire from engine.ts when a size-safe push exists.
 *  engine.ts: for each NPCS entry on the current map with sprite starting
 *  "npc/", spawnOf(MAPS[mapId], mark) and drawActor(`${id}-${wf}`).
 *  Skip: soldier1/2/3, cathleen, shinigami, chest, spawn, houseDoor,
 *  cageGate, reachStone (those keep special-case draws).
 */
export const PACK_NPC_SKIP = [
  "soldier1",
  "soldier2",
  "soldier3",
  "cathleen",
  "shinigami",
  "chest",
  "spawn",
  "houseDoor",
  "cageGate",
  "reachStone",
] as const;
