#!/usr/bin/env node
/**
 * FireRed-style Town Map generator foundation.
 *
 * Source of truth: content/world_map_layout.json
 * This intentionally renders a projection of the world graph rather than
 * replacing playable map data.
 */
import fs from "node:fs";
import path from "node:path";

const input = process.argv[2] ?? "content/world_map_layout.json";
const output = process.argv[3] ?? "docs/generated/sorrow-county-town-map.md";

const world = JSON.parse(fs.readFileSync(input, "utf8"));
const maps = world.maps;
const visible = Object.entries(maps).filter(([, map]) => map.active);

const graph = new Map();
for (const [id] of visible) graph.set(id, []);
for (const edge of world.connections) {
  if (!graph.has(edge.from) || !graph.has(edge.to)) continue;
  graph.get(edge.from).push({ id: edge.to, direction: edge.direction });
  graph.get(edge.to).push({ id: edge.from, direction: edge.direction });
}

const anchor = world.playerMarker.mapId;
const positions = new Map([[anchor, { x: 0, y: 0 }]]);
const queue = [anchor];
const offsets = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] };

while (queue.length) {
  const current = queue.shift();
  for (const next of graph.get(current) ?? []) {
    if (positions.has(next.id)) continue;
    const [dx, dy] = offsets[next.direction] ?? [0, 1];
    const p = positions.get(current);
    positions.set(next.id, { x: p.x + dx, y: p.y + dy });
    queue.push(next.id);
  }
}

const orphanMaps = visible.filter(([id]) => !positions.has(id)).map(([id]) => id);
const lines = [
  "# Sorrow County Town Map (generated)",
  "",
  "Legend: 💎 destination | ▫ travel area",
  "",
  "```text",
];

for (const [id, pos] of [...positions.entries()].sort((a, b) => a[1].y - b[1].y || a[1].x - b[1].x)) {
  const map = maps[id];
  const icon = id === anchor || /shrine|town|camp/i.test(map.label) ? "💎" : "▫";
  lines.push(`${icon} ${map.label} (${pos.x},${pos.y})`);
}
lines.push("```", "");
lines.push(`## Validation`, "");
lines.push(orphanMaps.length ? `Unreachable maps: ${orphanMaps.join(", ")}` : "All active maps connected.");

fs.mkdirSync(path.dirname(output), { recursive: true });
fs.writeFileSync(output, lines.join("\n"));
console.log(`Generated ${output}`);
