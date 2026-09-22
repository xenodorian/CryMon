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
  /* Destinations (plot hubs) — gem markers only */
  veld: { label: "CryTown", kind: "town", gem: true },
  camp: { label: "The Camp", kind: "camp", gem: true },
  grove: { label: "The Grove", kind: "landmark", gem: true },
  reach: { label: "The Reach", kind: "landmark", gem: true },
  heavenfall_shrine: { label: "Heavenfall Shrine", kind: "shrine", gem: true },
  quarry: { label: "The Quarry", kind: "cave", gem: true },
  /* Routes (travel corridors + borderline) — path only, no gem */
  forest: { label: "The Forest", kind: "route", gem: false },
  cliffs: { label: "The Cliffs", kind: "route", gem: false },
  marsh: { label: "The Marsh", kind: "route", gem: false },
  ruins: { label: "The Ruins", kind: "route", gem: false },
  gauntlet_route: { label: "Gauntlet", kind: "route", gem: false },
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
  ruins: { x: 2, y: 2 }, // east of the Grove
  gauntlet_route: { x: 0, y: 3 }, // south of the Grove
  reach: { x: 2, y: 3 }, // south of Ruins
  heavenfall_shrine: { x: 0, y: 4 }, // south of the Gauntlet
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

/* ========== Procedural tile terrain (FireRed-style region sheet) ==========
 * Tile codes:
 *  W water | L land | G grass | F forest | M marsh | C cliff | R road | S sand
 */
const TILE = { W: 0, L: 1, G: 2, F: 3, M: 4, C: 5, R: 6, S: 7 };
const TILE_NAME = ["W", "L", "G", "F", "M", "C", "R", "S"];

const nxs = [...positions.values()].map((p) => p.x);
const nys = [...positions.values()].map((p) => p.y);
const nMinX = Math.min(...nxs);
const nMaxX = Math.max(...nxs);
const nMinY = Math.min(...nys);
const nMaxY = Math.max(...nys);
// Each region cell expands to TILE_SCALE×TILE_SCALE pixels on the sheet
const TILE_SCALE = 8;
const MARGIN = 3;
const gridW = (nMaxX - nMinX + 1) * TILE_SCALE + MARGIN * 2;
const gridH = (nMaxY - nMinY + 1) * TILE_SCALE + MARGIN * 2;

function cellOrigin(rx, ry) {
  return {
    x: MARGIN + (rx - nMinX) * TILE_SCALE + Math.floor(TILE_SCALE / 2),
    y: MARGIN + (ry - nMinY) * TILE_SCALE + Math.floor(TILE_SCALE / 2),
  };
}

const grid = Array.from({ length: gridH }, () =>
  Array.from({ length: gridW }, () => TILE.W)
);

function inBounds(x, y) {
  return x >= 0 && y >= 0 && x < gridW && y < gridH;
}
function setTile(x, y, t) {
  if (inBounds(x, y)) grid[y][x] = t;
}
function stampDisk(cx, cy, r, tile, onlyIf) {
  for (let dy = -r; dy <= r; dy++) {
    for (let dx = -r; dx <= r; dx++) {
      if (dx * dx + dy * dy > r * r) continue;
      const x = cx + dx;
      const y = cy + dy;
      if (!inBounds(x, y)) continue;
      if (onlyIf && !onlyIf(grid[y][x])) continue;
      grid[y][x] = tile;
    }
  }
}

// 1) Mainland landmass covering all nodes (+margin)
for (let y = MARGIN - 1; y < gridH - (MARGIN - 1); y++) {
  for (let x = MARGIN - 1; x < gridW - (MARGIN - 1); x++) {
    // Irregular coast: push water inward on corners
    const edge =
      x <= MARGIN ||
      y <= MARGIN ||
      x >= gridW - MARGIN - 1 ||
      y >= gridH - MARGIN - 1;
    if (edge && ((x + y) % 5 === 0 || (x * 3 + y) % 7 === 0)) continue;
    grid[y][x] = TILE.L;
  }
}

// 2) Local terrain from node kind
const KIND_TILE = {
  town: TILE.G,
  camp: TILE.S,
  landmark: TILE.G,
  shrine: TILE.S,
  route: TILE.G,
};
for (const [id, pos] of positions) {
  const o = cellOrigin(pos.x, pos.y);
  const kind = kindOf(id);
  let base = KIND_TILE[kind] ?? TILE.G;
  if (id === "marsh") base = TILE.M;
  if (id === "cliffs" || id === "quarry") base = TILE.C;
  if (id === "forest" || id === "grove" || id === "gauntlet_route") base = TILE.F;
  if (id === "ruins" || id === "reach") base = TILE.S;
  stampDisk(o.x, o.y, id === "veld" ? 4 : 3, base, (t) => t !== TILE.W);
}

// 3) Roads along edges (Bresenham) — routes are the corridors
function carveRoad(x0, y0, x1, y1) {
  let dx = Math.abs(x1 - x0);
  let dy = Math.abs(y1 - y0);
  let sx = x0 < x1 ? 1 : -1;
  let sy = y0 < y1 ? 1 : -1;
  let err = dx - dy;
  let x = x0;
  let y = y0;
  for (;;) {
    for (let oy = -1; oy <= 1; oy++) {
      for (let ox = -1; ox <= 1; ox++) {
        if (Math.abs(ox) + Math.abs(oy) > 1) continue; // plus shape
        const tx = x + ox;
        const ty = y + oy;
        if (!inBounds(tx, ty)) continue;
        if (grid[ty][tx] === TILE.W) continue;
        grid[ty][tx] = TILE.R;
      }
    }
    if (x === x1 && y === y1) break;
    const e2 = 2 * err;
    if (e2 > -dy) {
      err -= dy;
      x += sx;
    }
    if (e2 < dx) {
      err += dx;
      y += sy;
    }
  }
}
for (const e of edges) {
  if (!positions.has(e.from) || !positions.has(e.to)) continue;
  const a = cellOrigin(positions.get(e.from).x, positions.get(e.from).y);
  const b = cellOrigin(positions.get(e.to).x, positions.get(e.to).y);
  carveRoad(a.x, a.y, b.x, b.y);
}

// 4) Pixel-art style dither on forests/marsh/cliffs
function dither(tile, fn) {
  for (let y = 0; y < gridH; y++) {
    for (let x = 0; x < gridW; x++) {
      if (grid[y][x] === tile && fn(x, y)) {
        /* keep as-is; drawing layer handles pattern */
      }
    }
  }
}
dither(TILE.F, () => true);

const terrain = {
  width: gridW,
  height: gridH,
  tileSize: 4, // display pixels per tile in static art
  tiles: grid.map((row) => row.map((t) => TILE_NAME[t]).join("")),
  legend: {
    W: "water",
    L: "land",
    G: "grass",
    F: "forest",
    M: "marsh",
    C: "cliff",
    R: "road",
    S: "sand",
  },
};

const playerMapId = world.playerMarker?.mapId ?? "veld";
const townMap = {
  version: 2,
  name: "Sorrow County",
  anchor,
  playerStartMap: playerMapId,
  nodes: regionNodes,
  edges: regionEdges,
  collapse: COLLAPSE,
  terrain,
  generatedFrom: input,
};
fs.writeFileSync(jsonOut, JSON.stringify(townMap, null, 2) + "\n");

// --- developer MD ---
const md = [];
md.push("# Sorrow County Town Map (generated)");
md.push("");
md.push(`Source: \`${input}\` → \`${jsonOut}\``);
md.push(`Anchor: **${labelOf(anchor)}** (\`${anchor}\`)`);
md.push(`Terrain grid: ${gridW}×${gridH} tiles (procedural)`);
md.push("");
md.push("## Destinations (gems) vs routes");
md.push("");
for (const [id, pos] of [...positions.entries()].sort(
  (a, b) => a[1].y - b[1].y || a[1].x - b[1].x
)) {
  md.push(`${isGem(id) ? "💎" : "·"} ${labelOf(id)}  (${pos.x},${pos.y}) [${kindOf(id)}]`);
}
md.push("");
md.push("## Connections");
md.push("");
for (const e of edges) {
  md.push(
    `- ${labelOf(e.from)} → ${labelOf(e.to)} [${e.direction}]${e.need ? ` need:${e.need}` : ""}`
  );
}
md.push("");
md.push("## Validation");
md.push("");
md.push(
  errors.length
    ? errors.map((e) => `- ERROR: ${e}`).join("\n")
    : "All region nodes reachable from CryTown."
);
fs.mkdirSync(path.dirname(mdOut), { recursive: true });
fs.writeFileSync(mdOut, md.join("\n") + "\n");

// --- Pixel-art tile SVG ---
const TS = 6; // px per terrain tile in SVG
const svgW = gridW * TS + 24;
const svgH = gridH * TS + 40;
const COLORS = {
  W: ["#3a6a9a", "#2a5a8a"],
  L: ["#6a9a4a", "#5a8a3a"],
  G: ["#7aba55", "#6aaa45"],
  F: ["#3d7a35", "#2d6a28"],
  M: ["#5a8a60", "#4a7a50"],
  C: ["#8a8a78", "#6a6a5a"],
  R: ["#e8d9a8", "#d0c090"],
  S: ["#d4c48a", "#c4b47a"],
};

function tileColor(ch, x, y) {
  const pair = COLORS[ch] || COLORS.L;
  // checker/dither for pixel feel
  return (x + y) % 2 === 0 ? pair[0] : pair[1];
}

const svg = [];
svg.push(`<?xml version="1.0" encoding="UTF-8"?>`);
svg.push(
  `<svg xmlns="http://www.w3.org/2000/svg" width="${svgW}" height="${svgH}" viewBox="0 0 ${svgW} ${svgH}" shape-rendering="crispEdges">`
);
svg.push(`  <rect width="100%" height="100%" fill="#1a2a18"/>`);
svg.push(
  `  <text x="${svgW / 2}" y="18" text-anchor="middle" fill="#e8f0d8" font-family="monospace" font-size="12">Sorrow County</text>`
);
const ox = 12;
const oy = 28;
for (let y = 0; y < gridH; y++) {
  for (let x = 0; x < gridW; x++) {
    const ch = TILE_NAME[grid[y][x]];
    // sub-pixel detail: 2x2 micro tiles inside each cell for forest/marsh
    if (ch === "F" || ch === "M" || ch === "C") {
      const hs = TS / 2;
      for (let sy = 0; sy < 2; sy++) {
        for (let sx = 0; sx < 2; sx++) {
          const c = tileColor(ch, x * 2 + sx, y * 2 + sy);
          svg.push(
            `  <rect x="${ox + x * TS + sx * hs}" y="${oy + y * TS + sy * hs}" width="${hs}" height="${hs}" fill="${c}"/>`
          );
        }
      }
    } else {
      svg.push(
        `  <rect x="${ox + x * TS}" y="${oy + y * TS}" width="${TS}" height="${TS}" fill="${tileColor(ch, x, y)}"/>`
      );
    }
  }
}
function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
// Gems on destinations
for (const [id, pos] of positions) {
  if (!isGem(id)) continue;
  const o = cellOrigin(pos.x, pos.y);
  const gx = ox + o.x * TS + TS / 2;
  const gy = oy + o.y * TS + TS / 2;
  svg.push(`  <circle cx="${gx}" cy="${gy}" r="5" fill="#1a4a6a"/>`);
  svg.push(
    `  <path d="M ${gx} ${gy - 4} L ${gx + 3.5} ${gy} L ${gx} ${gy + 4} L ${gx - 3.5} ${gy} Z" fill="#7ec8f0"/>`
  );
  svg.push(
    `  <text x="${gx}" y="${gy + 12}" text-anchor="middle" fill="#fff8e0" font-family="monospace" font-size="7">${esc(labelOf(id))}</text>`
  );
}
// Route labels (small)
for (const [id, pos] of positions) {
  if (isGem(id)) continue;
  const o = cellOrigin(pos.x, pos.y);
  const gx = ox + o.x * TS + TS / 2;
  const gy = oy + o.y * TS + TS / 2;
  svg.push(
    `  <text x="${gx}" y="${gy - 5}" text-anchor="middle" fill="#f0e8c8" font-family="monospace" font-size="6">${esc(labelOf(id))}</text>`
  );
}
svg.push(`</svg>`);
fs.mkdirSync(path.dirname(svgOut), { recursive: true });
fs.writeFileSync(svgOut, svg.join("\n") + "\n");

console.log(`Generated ${jsonOut}`);
console.log(`Generated ${mdOut}`);
console.log(`Generated ${svgOut}`);
console.log(`Terrain ${gridW}x${gridH} tiles`);
if (errors.length) {
  console.error("Validation:", errors.join("; "));
  process.exitCode = 1;
} else console.log("Validation: OK");
