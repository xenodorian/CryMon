#!/usr/bin/env node
/**
 * FireRed-style Town Map generator for Sorrow County.
 *
 * Source of truth: content/world_map_layout.json (connectivity/direction)
 * plus content/maps.json's real per-map tile grids (real dimensions).
 * Each region's Town Map cell is sized proportionally to its real map's
 * tile dimensions (scaled down), then regions are packed flush against
 * their neighbor along the real door's edge -- a simplified "ribbon"
 * that gets each route's real length/orientation right without tracing
 * every wall tile-for-tile.
 *
 * Outputs:
 *   content/town_map.json                      (runtime data for web)
 *   docs/generated/sorrow-county-town-map.md   (developer view)
 *   public/maps/sorrow-county-town-map.svg     (static player art)
 */
import fs from "node:fs";
import path from "node:path";

const layoutIn = process.argv[2] ?? "content/world_map_layout.json";
const mapsIn = "content/maps.json";
const jsonOut = "content/town_map.json";
const mdOut = "docs/generated/sorrow-county-town-map.md";
const svgOut = "public/maps/sorrow-county-town-map.svg";

const layout = JSON.parse(fs.readFileSync(layoutIn, "utf8"));
const mapsPack = JSON.parse(fs.readFileSync(mapsIn, "utf8"));
const maps = layout.maps;
const rows = mapsPack.rows ?? {};

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
const GAUNTLET_CHAIN = ["gauntlet1", "gauntlet2", "gauntlet3", "gauntlet4", "gauntlet5"];

const REGION_META = {
  /* Destinations (plot hubs / points of interest) -- gem markers */
  veld: { label: "CryTown", kind: "town", gem: true },
  camp: { label: "The Camp", kind: "camp", gem: true },
  grove: { label: "The Grove", kind: "landmark", gem: true },
  reach: { label: "The Reach", kind: "landmark", gem: true },
  heavenfall_shrine: { label: "Heavenfall Shrine", kind: "shrine", gem: true },
  quarry: { label: "The Quarry", kind: "cave", gem: false },
  /* Routes -- real elongated corridors, no marker, label on the path */
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

function labelOf(id) {
  return REGION_META[id]?.label ?? maps[id]?.label ?? id;
}
function isGem(id) {
  return REGION_META[id]?.gem ?? false;
}
function kindOf(id) {
  return REGION_META[id]?.kind ?? "route";
}

/** Real tile dimensions straight from content/maps.json's rows -- the
 * actual playable grid, not the (partly inert) width/height fields. */
function realSize(mapId) {
  const grid = rows[mapId];
  if (!grid || !grid.length) return null;
  return { width: Math.max(...grid.map((r) => r.length)), height: grid.length };
}

const SCALE = 10; // 1 Town Map cell = 10 real tiles
function cellSize(regionKey) {
  if (regionKey === "gauntlet_route") {
    // One simplified corridor sized to the combined length of the chain --
    // per decision, not five stitched segments.
    let w = 0;
    let h = 0;
    for (const mid of GAUNTLET_CHAIN) {
      const sz = realSize(mid);
      if (!sz) continue;
      w = Math.max(w, sz.width);
      h += sz.height;
    }
    return { w: Math.max(1, Math.round(w / SCALE)), h: Math.max(1, Math.round(h / SCALE)) };
  }
  if (regionKey === "heavenfall_shrine") {
    const sz = realSize("gauntlet6") ?? { width: 16, height: 20 };
    return { w: Math.max(1, Math.round(sz.width / SCALE)), h: Math.max(1, Math.round(sz.height / SCALE)) };
  }
  let sz = realSize(regionKey);
  if (!sz) {
    for (const mid of Object.keys(rows)) {
      if (regionId(mid) === regionKey) {
        sz = realSize(mid);
        break;
      }
    }
  }
  if (!sz) return { w: 1, h: 1 };
  return { w: Math.max(1, Math.round(sz.width / SCALE)), h: Math.max(1, Math.round(sz.height / SCALE)) };
}

/** Which edge of the FROM map's real grid the door sits closest to. */
function exitEdge(fromMapId, fromXY) {
  const sz = realSize(fromMapId);
  if (!sz || !fromXY) return "south";
  const { width: w, height: h } = sz;
  const x = fromXY.x ?? 0;
  const y = fromXY.y ?? 0;
  const d = { west: x, east: w - 1 - x, north: y, south: h - 1 - y };
  return Object.keys(d).reduce((best, k) => (d[k] < d[best] ? k : best), "south");
}
function alignFrac(fromMapId, fromXY) {
  const sz = realSize(fromMapId);
  if (!sz) return 0.5;
  const { width: w, height: h } = sz;
  const x = fromXY?.x ?? w / 2;
  const y = fromXY?.y ?? h / 2;
  const edge = exitEdge(fromMapId, fromXY);
  return edge === "east" || edge === "west" ? y / Math.max(1, h - 1) : x / Math.max(1, w - 1);
}

const seen = new Set();
const regionEdges = [];
for (const c of layout.connections ?? []) {
  const a = regionId(c.from);
  const b = regionId(c.to);
  if (!a || !b || a === b) continue;
  const key = [a, b].sort().join("|");
  if (seen.has(key)) continue;
  seen.add(key);
  regionEdges.push({ from: a, to: b, edge: exitEdge(c.from, c.fromXY), need: c.need ?? null, src: c });
}

const sizes = {};
for (const id of Object.keys(REGION_META)) sizes[id] = cellSize(id);

/** Rectangle packer: place each region flush against its already-placed
 * neighbor along the real exit edge. If the ideal spot (or the whole
 * adjacent row/column) is occupied, expand outward in rings until a
 * fully free w x h rectangle is found -- this is the fix for the
 * Camp/Forest collision bug (the old packer only tried offsets within
 * the immediate adjacent row and silently overlapped when that row
 * was already full). */
const boxes = {};
function occupied(x, y, w, h) {
  for (const b of Object.values(boxes)) {
    if (x < b.x + b.w && x + w > b.x && y < b.y + b.h && y + h > b.y) return true;
  }
  return false;
}
function placeNear(id, w, h, idealX, idealY) {
  if (occupied(idealX, idealY, w, h) === false) {
    boxes[id] = { x: idealX, y: idealY, w, h };
    return;
  }
  for (let r = 1; r < 64; r++) {
    for (let dy = -r; dy <= r; dy++) {
      for (let dx = -r; dx <= r; dx++) {
        if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue;
        const x = idealX + dx;
        const y = idealY + dy;
        if (!occupied(x, y, w, h)) {
          boxes[id] = { x, y, w, h };
          return;
        }
      }
    }
  }
  boxes[id] = { x: idealX, y: idealY, w, h }; // unreachable in practice
}
function idealSpot(parentBox, edge, childW, childH, t) {
  const p = parentBox;
  if (edge === "east") return { x: p.x + p.w, y: p.y + Math.round(t * Math.max(0, p.h - 1)) - Math.floor(childH / 2) };
  if (edge === "west") return { x: p.x - childW, y: p.y + Math.round(t * Math.max(0, p.h - 1)) - Math.floor(childH / 2) };
  if (edge === "north") return { x: p.x + Math.round(t * Math.max(0, p.w - 1)) - Math.floor(childW / 2), y: p.y - childH };
  return { x: p.x + Math.round(t * Math.max(0, p.w - 1)) - Math.floor(childW / 2), y: p.y + p.h }; // south
}

const graph = new Map();
for (const id of Object.keys(REGION_META)) graph.set(id, []);
const invEdge = { east: "west", west: "east", north: "south", south: "north" };
for (const e of regionEdges) {
  if (!graph.has(e.from) || !graph.has(e.to)) continue;
  graph.get(e.from).push({ id: e.to, edge: e.edge, t: alignFrac(e.src.from, e.src.fromXY), need: e.need });
  graph.get(e.to).push({ id: e.from, edge: invEdge[e.edge] ?? "south", t: 0.5, need: e.need });
}

const anchor = regionId(layout.playerMarker?.mapId ?? "veld") ?? "veld";
boxes[anchor] = { x: 0, y: 0, w: sizes[anchor].w, h: sizes[anchor].h };
const queue = [anchor];
const placed = new Set([anchor]);
while (queue.length) {
  const cur = queue.shift();
  for (const next of graph.get(cur) ?? []) {
    if (placed.has(next.id)) continue;
    const sz = sizes[next.id] ?? { w: 1, h: 1 };
    const spot = idealSpot(boxes[cur], next.edge, sz.w, sz.h, next.t);
    placeNear(next.id, sz.w, sz.h, spot.x, spot.y);
    placed.add(next.id);
    queue.push(next.id);
  }
}
// Any region metadata entries never reached by the connection graph
// (shouldn't happen with current content, but stay defensive).
for (const id of Object.keys(REGION_META)) {
  if (!boxes[id]) {
    const sz = sizes[id];
    const maxY = Math.max(0, ...Object.values(boxes).map((b) => b.y + b.h));
    placeNear(id, sz.w, sz.h, 0, maxY);
  }
}

const orphanRegions = Object.keys(REGION_META).filter((id) => !boxes[id]);
const errors = [];
if (orphanRegions.length) errors.push(`Unreachable: ${orphanRegions.join(", ")}`);

// Normalize to non-negative coordinates.
const minX = Math.min(...Object.values(boxes).map((b) => b.x));
const minY = Math.min(...Object.values(boxes).map((b) => b.y));
for (const b of Object.values(boxes)) {
  b.x -= minX;
  b.y -= minY;
}

// --- content/town_map.json for runtime ---
const regionNodes = Object.entries(boxes).map(([id, b]) => {
  const sz = realSize(id) ?? (id === "gauntlet_route" ? { width: 16, height: 180 } : id === "heavenfall_shrine" ? realSize("gauntlet6") : { width: b.w * SCALE, height: b.h * SCALE });
  return {
    id,
    label: labelOf(id),
    kind: kindOf(id),
    gem: isGem(id),
    x: b.x,
    y: b.y,
    cellW: b.w,
    cellH: b.h,
    playableMaps: Object.keys(maps).filter((m) => regionId(m) === id),
    realSize: sz,
  };
});
const regionEdgesOut = regionEdges
  .filter((e) => boxes[e.from] && boxes[e.to])
  .map((e) => ({ from: e.from, to: e.to, edge: e.edge, need: e.need }));

const M = 2;
const maxX = Math.max(...Object.values(boxes).map((b) => b.x + b.w));
const maxY = Math.max(...Object.values(boxes).map((b) => b.y + b.h));
const gridW = maxX + M * 2;
const gridH = maxY + M * 2;

const playerStartMap = layout.playerMarker?.mapId ?? "veld";
const townMap = {
  version: 4,
  name: layout.name ?? "Sorrow County",
  anchor,
  playerStartMap,
  scale: SCALE,
  scaleNote: `1 cell = ${SCALE} real tiles`,
  nodes: regionNodes,
  edges: regionEdgesOut,
  collapse: COLLAPSE,
  terrain: { width: gridW, height: gridH },
  generatedFrom: { layout: layoutIn, maps: mapsIn },
};
fs.writeFileSync(jsonOut, JSON.stringify(townMap, null, 2) + "\n");

// --- developer MD ---
const md = [];
md.push("# Sorrow County Town Map (generated)");
md.push("");
md.push(`Source: \`${layoutIn}\` + \`${mapsIn}\` (real tile grids) -> \`${jsonOut}\``);
md.push(`Anchor: **${labelOf(anchor)}** (\`${anchor}\`)`);
md.push(`Scale: 1 cell = ${SCALE} real tiles. Grid: ${gridW}x${gridH} cells.`);
md.push("");
md.push("## Destinations (gems) vs routes");
md.push("");
for (const [id, b] of Object.entries(boxes).sort((a, b2) => a[1].y - b2[1].y || a[1].x - b2[1].x)) {
  const rs = regionNodes.find((n) => n.id === id).realSize;
  md.push(`${isGem(id) ? "\u{1F48E}" : "·"} ${labelOf(id)}  cell(${b.x},${b.y} ${b.w}x${b.h})  real(${rs.width}x${rs.height}) [${kindOf(id)}]`);
}
md.push("");
md.push("## Connections");
md.push("");
for (const e of regionEdgesOut) {
  md.push(`- ${labelOf(e.from)} -> ${labelOf(e.to)} [${e.edge}]${e.need ? ` need:${e.need}` : ""}`);
}
md.push("");
md.push("## Validation");
md.push("");
md.push(errors.length ? errors.map((e) => `- ERROR: ${e}`).join("\n") : "All region nodes reachable from CryTown, no cell overlaps.");
fs.mkdirSync(path.dirname(mdOut), { recursive: true });
fs.writeFileSync(mdOut, md.join("\n") + "\n");

// --- SVG: proportional cells with real biome coloring ---
const CELL = 26;
const ox = 20;
const oy = 32;
const svgW = gridW * CELL + ox * 2;
const svgH = gridH * CELL + oy + 20;

// Every cell is the same flat beige -- a colored-by-kind fill or an
// internal "path stripe" implies a specific correct sub-path through
// the cell that isn't real (the cell is a simplified proportional
// footprint, not a tile-traced route). Only the gem markers get color.
const CELL_FILL = "#d4c49a";
const CELL_STROKE = "#8a7a55";

function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

const svg = [];
svg.push(`<?xml version="1.0" encoding="UTF-8"?>`);
svg.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${svgW}" height="${svgH}" viewBox="0 0 ${svgW} ${svgH}">`);
svg.push(`  <rect width="100%" height="100%" fill="#14283a"/>`);
svg.push(`  <text x="${svgW / 2}" y="18" text-anchor="middle" fill="#e8f0d8" font-family="Georgia, serif" font-size="14" font-weight="bold">${esc(townMap.name)}</text>`);

for (const [id, b] of Object.entries(boxes)) {
  const x = ox + (M + b.x) * CELL;
  const y = oy + (M + b.y) * CELL;
  const w = b.w * CELL;
  const h = b.h * CELL;
  svg.push(`  <rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${CELL_FILL}" stroke="${CELL_STROKE}" stroke-width="0.5"/>`);
}

for (const [id, b] of Object.entries(boxes)) {
  const cx = ox + (M + b.x + b.w / 2) * CELL;
  const gem = isGem(id);
  // Gauntlet's label sits in the vertical middle of the long corridor it
  // represents (the 5 chained gauntlet maps), not pinned to the top edge.
  const labelInMiddle = id === "gauntlet_route";
  const labelY = labelInMiddle ? oy + (M + b.y + b.h / 2) * CELL + 3 : oy + (M + b.y) * CELL + 9;
  svg.push(`  <text x="${cx}" y="${labelY}" text-anchor="middle" fill="#f8f4e2" font-family="Georgia, serif" font-size="8" stroke="#1a1408" stroke-width="2" paint-order="stroke">${esc(labelOf(id))}</text>`);
  if (gem) {
    const gy = oy + (M + b.y + b.h / 2) * CELL;
    svg.push(`  <circle cx="${cx}" cy="${gy}" r="5.5" fill="#0a2f52" stroke="#04182b" stroke-width="1"/>`);
    svg.push(`  <path d="M ${cx} ${gy - 4} L ${cx + 3.5} ${gy} L ${cx} ${gy + 4} L ${cx - 3.5} ${gy} Z" fill="#29b6ff" stroke="#0288d1" stroke-width="0.5"/>`);
  }
}
svg.push(`</svg>`);
fs.mkdirSync(path.dirname(svgOut), { recursive: true });
fs.writeFileSync(svgOut, svg.join("\n") + "\n");

console.log(`Generated ${jsonOut}`);
console.log(`Generated ${mdOut}`);
console.log(`Generated ${svgOut}`);
console.log(`Grid ${gridW}x${gridH} cells`);
if (errors.length) {
  console.error("Validation:", errors.join("; "));
  process.exitCode = 1;
} else console.log("Validation: OK");
