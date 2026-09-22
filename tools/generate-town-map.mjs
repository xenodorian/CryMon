#!/usr/bin/env node
/**
 * FireRed-style Town Map generator for Sorrow County.
 *
 * Source of truth: content/world_map_layout.json (+ optional warp edges).
 * Phases: graph extract → collapse interiors → auto layout → validate → render.
 *
 * Usage:
 *   node tools/generate-town-map.mjs
 *   node tools/generate-town-map.mjs content/world_map_layout.json
 *
 * Outputs:
 *   docs/generated/sorrow-county-town-map.md   (developer view)
 *   public/maps/sorrow-county-town-map.svg     (player view)
 */
import fs from "node:fs";
import path from "node:path";

const input = process.argv[2] ?? "content/world_map_layout.json";
const mdOut = process.argv[3] ?? "docs/generated/sorrow-county-town-map.md";
const svgOut = process.argv[4] ?? "public/maps/sorrow-county-town-map.svg";

const world = JSON.parse(fs.readFileSync(input, "utf8"));
const maps = world.maps;

/** Collapse rules (plan Phase 2): hide interiors; fold gauntlet floors. */
const COLLAPSE = {
  // playable id → region node id (or null to hide entirely as interior)
  house: "veld", // HOME folds into CryTown
  gauntlet1: "gauntlet_route",
  gauntlet2: "gauntlet_route",
  gauntlet3: "gauntlet_route",
  gauntlet4: "gauntlet_route",
  gauntlet5: "gauntlet_route",
  gauntlet6: "heavenfall_shrine",
  gauntlet: null, // legacy inactive
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
  if (Object.prototype.hasOwnProperty.call(COLLAPSE, mapId)) {
    return COLLAPSE[mapId];
  }
  if (!maps[mapId] || maps[mapId].active === false) return null;
  return mapId;
}

// --- Phase 1: graph from connections ---
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

// dedupe undirected pairs but keep one directed for layout bias
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
// ensure region meta nodes that appear only as collapse targets
for (const id of Object.values(COLLAPSE)) {
  if (id) nodes.add(id);
}
for (const id of Object.keys(maps)) {
  const r = regionId(id);
  if (r) nodes.add(r);
}

const graph = new Map();
for (const id of nodes) graph.set(id, []);
for (const e of edges) {
  graph.get(e.from).push({ id: e.to, direction: e.direction, need: e.need });
  const inv = { up: "down", down: "up", left: "right", right: "left" };
  graph.get(e.to).push({
    id: e.from,
    direction: inv[e.direction] ?? "up",
    need: e.need,
  });
}

// --- Phase 3: layout (CryTown = veld anchor) ---
const anchor = regionId(world.playerMarker?.mapId ?? "veld") ?? "veld";
const positions = new Map([[anchor, { x: 0, y: 0 }]]);
const queue = [anchor];
const offsets = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] };
const occupied = new Set(["0,0"]);

function place(id, preferred) {
  let { x, y } = preferred;
  if (!occupied.has(`${x},${y}`)) {
    occupied.add(`${x},${y}`);
    positions.set(id, { x, y });
    return;
  }
  // spiral search for free cell
  for (let r = 1; r < 12; r++) {
    for (let dy = -r; dy <= r; dy++) {
      for (let dx = -r; dx <= r; dx++) {
        if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue;
        const nx = preferred.x + dx;
        const ny = preferred.y + dy;
        const key = `${nx},${ny}`;
        if (!occupied.has(key)) {
          occupied.add(key);
          positions.set(id, { x: nx, y: ny });
          return;
        }
      }
    }
  }
  positions.set(id, preferred);
}

while (queue.length) {
  const current = queue.shift();
  for (const next of graph.get(current) ?? []) {
    if (positions.has(next.id)) continue;
    const [dx, dy] = offsets[next.direction] ?? [0, 1];
    const p = positions.get(current);
    place(next.id, { x: p.x + dx, y: p.y + dy });
    queue.push(next.id);
  }
}

// orphans (active maps that collapse to a region never placed)
const orphanRegions = [...nodes].filter((id) => !positions.has(id));
const hiddenInteriors = Object.entries(COLLAPSE)
  .filter(([, v]) => v === null)
  .map(([k]) => k);
const collapsedInto = {};
for (const [src, dest] of Object.entries(COLLAPSE)) {
  if (!dest) continue;
  (collapsedInto[dest] ??= []).push(src);
}

// --- Phase 4: validation ---
const errors = [];
if (orphanRegions.length) {
  errors.push(`Unreachable region nodes: ${orphanRegions.join(", ")}`);
}
// dead-end warning: leaf that is not a landmark/shrine
for (const id of positions.keys()) {
  const deg = (graph.get(id) ?? []).length;
  const meta = REGION_META[id] ?? { kind: "route", gem: false };
  if (deg === 0) errors.push(`Isolated node: ${id}`);
  if (deg === 1 && meta.kind === "route" && id !== "gauntlet_route") {
    // soft note only in developer view
  }
}

// --- Phase 5: render ---
function labelOf(id) {
  return REGION_META[id]?.label ?? maps[id]?.label ?? id;
}
function isGem(id) {
  return REGION_META[id]?.gem ?? false;
}

// Developer markdown
const md = [];
md.push("# Sorrow County Town Map (generated)");
md.push("");
md.push(`Source: \`${input}\``);
md.push(`Anchor: **${labelOf(anchor)}** (\`${anchor}\`)`);
md.push("");
md.push("## Player projection");
md.push("");
md.push("Legend: 💎 town / camp / shrine | ▫ route / travel");
md.push("");
md.push("```text");
const sorted = [...positions.entries()].sort(
  (a, b) => a[1].y - b[1].y || a[1].x - b[1].x
);
for (const [id, pos] of sorted) {
  const icon = isGem(id) ? "💎" : "▫";
  md.push(`${icon} ${labelOf(id)}  (${pos.x},${pos.y})`);
}
md.push("```");
md.push("");
md.push("## Connections (region graph)");
md.push("");
for (const e of edges) {
  md.push(
    `- ${labelOf(e.from)} → ${labelOf(e.to)} [${e.direction}]${e.need ? ` need:${e.need}` : ""} _(${e.source})_`
  );
}
md.push("");
md.push("## Collapse rules applied");
md.push("");
for (const [dest, srcs] of Object.entries(collapsedInto)) {
  md.push(`- ${srcs.join(", ")} → **${labelOf(dest)}** (\`${dest}\`)`);
}
if (hiddenInteriors.length) {
  md.push(`- Hidden: ${hiddenInteriors.join(", ")}`);
}
md.push("");
md.push("## Validation");
md.push("");
if (errors.length === 0) md.push("All region nodes reachable from CryTown.");
else errors.forEach((e) => md.push(`- ERROR: ${e}`));
md.push("");
md.push("## Developer: playable maps → region");
md.push("");
for (const id of Object.keys(maps).sort()) {
  const r = regionId(id);
  md.push(`- \`${id}\` → ${r ? `\`${r}\` (${labelOf(r)})` : "_hidden_"}`);
}

fs.mkdirSync(path.dirname(mdOut), { recursive: true });
fs.writeFileSync(mdOut, md.join("\n") + "\n");

// Player SVG (beige routes, gem landmarks)
const xs = [...positions.values()].map((p) => p.x);
const ys = [...positions.values()].map((p) => p.y);
const minX = Math.min(...xs);
const maxX = Math.max(...xs);
const minY = Math.min(...ys);
const maxY = Math.max(...ys);
const cell = 72;
const pad = 48;
const width = (maxX - minX + 1) * cell + pad * 2;
const height = (maxY - minY + 1) * cell + pad * 2;
const px = (x) => pad + (x - minX) * cell + cell / 2;
const py = (y) => pad + (y - minY) * cell + cell / 2;

const svg = [];
svg.push(`<?xml version="1.0" encoding="UTF-8"?>`);
svg.push(
  `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">`
);
svg.push(`  <rect width="100%" height="100%" fill="#2a3a28"/>`);
svg.push(`  <text x="${pad}" y="28" fill="#e8e4d0" font-family="monospace" font-size="16">Sorrow County</text>`);

// edges first
for (const e of edges) {
  if (!positions.has(e.from) || !positions.has(e.to)) continue;
  const a = positions.get(e.from);
  const b = positions.get(e.to);
  svg.push(
    `  <line x1="${px(a.x)}" y1="${py(a.y)}" x2="${px(b.x)}" y2="${py(b.y)}" stroke="#c4b896" stroke-width="6" stroke-linecap="round"/>`
  );
}

// nodes
for (const [id, pos] of positions) {
  const x = px(pos.x);
  const y = py(pos.y);
  const gem = isGem(id);
  if (gem) {
    // diamond gem
    svg.push(
      `  <path d="M ${x} ${y - 14} L ${x + 12} ${y} L ${x} ${y + 14} L ${x - 12} ${y} Z" fill="#5ec8ff" stroke="#1a4a6a" stroke-width="2"/>`
    );
  } else {
    svg.push(
      `  <rect x="${x - 18}" y="${y - 12}" width="36" height="24" rx="3" fill="#d9cba8" stroke="#8a7a55" stroke-width="2"/>`
    );
  }
  const name = labelOf(id);
  svg.push(
    `  <text x="${x}" y="${y + 28}" text-anchor="middle" fill="#f0ecd8" font-family="monospace" font-size="11">${escapeXml(name)}</text>`
  );
}
svg.push(`</svg>`);

function escapeXml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

fs.mkdirSync(path.dirname(svgOut), { recursive: true });
fs.writeFileSync(svgOut, svg.join("\n") + "\n");
console.log(`Generated ${mdOut}`);
console.log(`Generated ${svgOut}`);
if (errors.length) {
  console.error("Validation issues:", errors.join("; "));
  process.exitCode = 1;
} else {
  console.log("Validation: OK");
}
