#!/usr/bin/env node
/**
 * FireRed-style Town Map generator for Sorrow County.
 *
 * Source of truth: content/world_map_layout.json
 * Phases: graph → collapse → layout → validate → render
 *
 * Outputs:
 *   content/town_map.json                      (runtime data for web/DC)
 *   docs/generated/sorrow-county-town-map.md   (developer view)
 *   public/maps/sorrow-county-town-map.svg     (static player art)
 */
import fs from "node:fs";
import path from "node:path";

const input = process.argv[2] ?? "content/world_map_layout.json";
const jsonOut = "content/town_map.json";
const mdOut = "docs/generated/sorrow-county-town-map.md";
const svgOut = "public/maps/sorrow-county-town-map.svg";

const world = JSON.parse(fs.readFileSync(input, "utf8"));
const maps = world.maps;

/** Phase 2 collapse: interiors fold into parent landmarks. */
const COLLAPSE = {
  house: "veld",
  gauntlet1: "gauntlet_route",
  gauntlet2: "gauntlet_route",
  gauntlet3: "gauntlet_route",
  gauntlet4: "gauntlet_route",
  gauntlet5: "gauntlet_route",
  gauntlet6: "heavenfall_shrine",
  gauntlet: null,
};

const REGION_META = {
  veld: { label: "CryTown", kind: "town", gem: true },
  camp: { label: "The Camp", kind: "camp", gem: true },
  forest: { label: "The Forest", kind: "route", gem: false },
  grove: { label: "The Grove", kind: "route", gem: false },
  cliffs: { label: "The Cliffs", kind: "route", gem: false },
  marsh: { label: "The Marsh", kind: "route", gem: false },
  quarry: { label: "The Quarry", kind: "cave", gem: false },
  ruins: { label: "The Ruins", kind: "route", gem: false },
  reach: { label: "The Reach", kind: "route", gem: false },
  gauntlet_route: { label: "Gauntlet", kind: "gauntlet", gem: false },
  heavenfall_shrine: { label: "Heavenfall Shrine", kind: "shrine", gem: true },
};

function regionId(mapId) {
  if (Object.prototype.hasOwnProperty.call(COLLAPSE, mapId)) return COLLAPSE[mapId];
  if (!maps[mapId] || maps[mapId].active === false) return null;
  return mapId;
}

const rawEdges = [];
for (const e of world.connections ?? []) {
  const a = regionId(e.from);
  const b = regionId(e.to);
  if (!a || !b || a === b) continue;
  rawEdges.push({
    from: a,
    to: b,
    direction: e.direction ?? "down",
    need: e.need ?? null,
    source: `${e.from}→${e.to}`,
  });
}

const edgeKey = (a, b) => [a, b].sort().join("|");
const seen = new Set();
const edges = [];
for (const e of rawEdges) {
  const k = edgeKey(e.from, e.to);
  if (seen.has(k)) continue;
  seen.add(k);
  edges.push(e);
}

const nodes = new Set();
for (const e of edges) {
  nodes.add(e.from);
  nodes.add(e.to);
}
for (const id of Object.values(COLLAPSE)) if (id) nodes.add(id);
for (const id of Object.keys(maps)) {
  const r = regionId(id);
  if (r) nodes.add(r);
}

const graph = new Map();
for (const id of nodes) graph.set(id, []);
const invDir = { up: "down", down: "up", left: "right", right: "left" };
for (const e of edges) {
  graph.get(e.from).push({ id: e.to, direction: e.direction, need: e.need });
  graph.get(e.to).push({
    id: e.from,
    direction: invDir[e.direction] ?? "up",
    need: e.need,
  });
}

/** Phase 3: directional layout with collision resolve.
 * Prefer placing each neighbor along the recorded edge direction from parent.
 * Also seed known branches from CryTown for stable geography. */
const anchor = regionId(world.playerMarker?.mapId ?? "veld") ?? "veld";
const offsets = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] };

/** Hand-tuned seed overrides (still derived from world directions; only
 *  fixes ambiguity when multiple edges leave the same node downward). */
const SEED = {
  veld: { x: 0, y: 0 },
  camp: { x: -2, y: 0 }, // west of town
  cliffs: { x: 2, y: 0 }, // east
  forest: { x: 0, y: 1 }, // south
  marsh: { x: -2, y: 1 },
  quarry: { x: 2, y: 1 },
  grove: { x: 0, y: 2 },
  gauntlet_route: { x: -2, y: 2 },
  ruins: { x: 0, y: 3 },
  heavenfall_shrine: { x: -2, y: 3 },
  reach: { x: 0, y: 4 },
};

const positions = new Map();
const occupied = new Set();

function placeAt(id, x, y) {
  if (positions.has(id)) return;
  let nx = x;
  let ny = y;
  if (occupied.has(`${nx},${ny}`)) {
    outer: for (let r = 1; r < 16; r++) {
      for (let dy = -r; dy <= r; dy++) {
        for (let dx = -r; dx <= r; dx++) {
          if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue;
          const tx = x + dx;
          const ty = y + dy;
          if (!occupied.has(`${tx},${ty}`)) {
            nx = tx;
            ny = ty;
            break outer;
          }
        }
      }
    }
  }
  occupied.add(`${nx},${ny}`);
  positions.set(id, { x: nx, y: ny });
}

// Seed first
for (const [id, p] of Object.entries(SEED)) {
  if (nodes.has(id)) placeAt(id, p.x, p.y);
}
// BFS for any remaining
const queue = [...positions.keys()];
while (queue.length) {
  const current = queue.shift();
  for (const next of graph.get(current) ?? []) {
    if (positions.has(next.id)) continue;
    const [dx, dy] = offsets[next.direction] ?? [0, 1];
    const p = positions.get(current);
    placeAt(next.id, p.x + dx, p.y + dy);
    queue.push(next.id);
  }
}

const orphanRegions = [...nodes].filter((id) => !positions.has(id));
const collapsedInto = {};
for (const [src, dest] of Object.entries(COLLAPSE)) {
  if (!dest) continue;
  (collapsedInto[dest] ??= []).push(src);
}
const errors = [];
if (orphanRegions.length) errors.push(`Unreachable: ${orphanRegions.join(", ")}`);
for (const id of positions.keys()) {
  if ((graph.get(id) ?? []).length === 0) errors.push(`Isolated: ${id}`);
}

function labelOf(id) {
  return REGION_META[id]?.label ?? maps[id]?.label ?? id;
}
function isGem(id) {
  return REGION_META[id]?.gem ?? false;
}
function kindOf(id) {
  return REGION_META[id]?.kind ?? "route";
}

// --- content/town_map.json for runtime ---
const regionNodes = [...positions.entries()].map(([id, pos]) => ({
  id,
  label: labelOf(id),
  kind: kindOf(id),
  gem: isGem(id),
  x: pos.x,
  y: pos.y,
  playableMaps: Object.keys(maps).filter((m) => regionId(m) === id),
}));
const regionEdges = edges.map((e) => ({
  from: e.from,
  to: e.to,
  direction: e.direction,
  need: e.need,
}));
const playerMapId = world.playerMarker?.mapId ?? "veld";
const townMap = {
  version: 1,
  name: "Sorrow County",
  anchor,
  playerStartMap: playerMapId,
  nodes: regionNodes,
  edges: regionEdges,
  collapse: COLLAPSE,
  generatedFrom: input,
};
fs.writeFileSync(jsonOut, JSON.stringify(townMap, null, 2) + "\n");

// --- developer MD ---
const md = [];
md.push("# Sorrow County Town Map (generated)");
md.push("");
md.push(`Source: \`${input}\` → \`${jsonOut}\``);
md.push(`Anchor: **${labelOf(anchor)}** (\`${anchor}\`)`);
md.push("");
md.push("## Player projection");
md.push("");
md.push("```text");
for (const [id, pos] of [...positions.entries()].sort(
  (a, b) => a[1].y - b[1].y || a[1].x - b[1].x
)) {
  md.push(`${isGem(id) ? "💎" : "▫"} ${labelOf(id)}  (${pos.x},${pos.y})`);
}
md.push("```");
md.push("");
md.push("## Connections");
md.push("");
for (const e of edges) {
  md.push(
    `- ${labelOf(e.from)} → ${labelOf(e.to)} [${e.direction}]${e.need ? ` need:${e.need}` : ""}`
  );
}
md.push("");
md.push("## Collapse");
md.push("");
for (const [dest, srcs] of Object.entries(collapsedInto)) {
  md.push(`- ${srcs.join(", ")} → **${labelOf(dest)}**`);
}
md.push("");
md.push("## Validation");
md.push("");
md.push(errors.length ? errors.map((e) => `- ERROR: ${e}`).join("\n") : "All region nodes reachable from CryTown.");
fs.mkdirSync(path.dirname(mdOut), { recursive: true });
fs.writeFileSync(mdOut, md.join("\n") + "\n");

// --- FireRed-ish SVG ---
const xs = [...positions.values()].map((p) => p.x);
const ys = [...positions.values()].map((p) => p.y);
const minX = Math.min(...xs);
const maxX = Math.max(...xs);
const minY = Math.min(...ys);
const maxY = Math.max(...ys);
const cell = 80;
const pad = 56;
const width = (maxX - minX + 1) * cell + pad * 2;
const height = (maxY - minY + 1) * cell + pad * 2 + 24;
const px = (x) => pad + (x - minX) * cell + cell / 2;
const py = (y) => pad + 16 + (y - minY) * cell + cell / 2;

function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

const svg = [];
svg.push(`<?xml version="1.0" encoding="UTF-8"?>`);
svg.push(
  `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">`
);
// parchment background
svg.push(`  <rect width="100%" height="100%" fill="#3d5a3a"/>`);
svg.push(`  <rect x="12" y="12" width="${width - 24}" height="${height - 24}" rx="8" fill="#c9b896" stroke="#6b5a3e" stroke-width="4"/>`);
svg.push(`  <rect x="20" y="20" width="${width - 40}" height="${height - 40}" rx="4" fill="#e8dcc0"/>`);
svg.push(
  `  <text x="${width / 2}" y="42" text-anchor="middle" fill="#4a3a28" font-family="Georgia, serif" font-size="18" font-weight="bold">Sorrow County</text>`
);

for (const e of edges) {
  if (!positions.has(e.from) || !positions.has(e.to)) continue;
  const a = positions.get(e.from);
  const b = positions.get(e.to);
  svg.push(
    `  <line x1="${px(a.x)}" y1="${py(a.y)}" x2="${px(b.x)}" y2="${py(b.y)}" stroke="#b8a878" stroke-width="10" stroke-linecap="round"/>`
  );
  svg.push(
    `  <line x1="${px(a.x)}" y1="${py(a.y)}" x2="${px(b.x)}" y2="${py(b.y)}" stroke="#f0e6c8" stroke-width="4" stroke-linecap="round"/>`
  );
}

for (const [id, pos] of positions) {
  const x = px(pos.x);
  const y = py(pos.y);
  if (isGem(id)) {
    svg.push(
      `  <circle cx="${x}" cy="${y}" r="16" fill="#4a90c8" stroke="#1a3a5a" stroke-width="2"/>`
    );
    svg.push(
      `  <path d="M ${x} ${y - 10} L ${x + 9} ${y} L ${x} ${y + 10} L ${x - 9} ${y} Z" fill="#7ec8f0" stroke="#2a5a7a" stroke-width="1"/>`
    );
  } else {
    svg.push(
      `  <rect x="${x - 20}" y="${y - 12}" width="40" height="24" rx="2" fill="#d4c49a" stroke="#8a7a55" stroke-width="2"/>`
    );
  }
  svg.push(
    `  <text x="${x}" y="${y + 30}" text-anchor="middle" fill="#3a2a18" font-family="Georgia, serif" font-size="11">${esc(labelOf(id))}</text>`
  );
}
svg.push(`</svg>`);
fs.mkdirSync(path.dirname(svgOut), { recursive: true });
fs.writeFileSync(svgOut, svg.join("\n") + "\n");

console.log(`Generated ${jsonOut}`);
console.log(`Generated ${mdOut}`);
console.log(`Generated ${svgOut}`);
if (errors.length) {
  console.error("Validation:", errors.join("; "));
  process.exitCode = 1;
} else console.log("Validation: OK");
