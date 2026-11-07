// Halftone map illustrations in the style of the zhol decks.
// Geography: Natural Earth via world-atlas (countries-10m). Routes: zhol/data/lanes.json.
// Usage: node scripts/maps/make_maps.mjs   (writes site/assets/img/audience-map.svg)
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { geoBounds, geoConicConformal, geoPath } from "d3-geo";
import { feature } from "topojson-client";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "../..");
const topo = JSON.parse(readFileSync(resolve(here, "node_modules/world-atlas/countries-50m.json"), "utf8"));
const countries = feature(topo, topo.objects.countries);
const lanes = JSON.parse(readFileSync(resolve(root, "zhol/data/lanes.json"), "utf8")).lanes;
const chokes = JSON.parse(readFileSync(resolve(root, "zhol/data/chokepoints.json"), "utf8"));

const PAL = { ink: "#352b28", red: "#a2311e", teal: "#2f7f86", tealLight: "#7fb7b6", paper: "#f6f3ea", muted: "#857b73" };
// ISO numeric ids in world-atlas
const FOCUS = new Set(["380", "040", "276", "756", "250", "705", "438", "674", "336"]); // IT AT DE CH FR SI LI SM VA
const NEAR = new Set(["203", "616", "191", "348", "070", "008", "499", "688", "056", "442", "528", "724", "020", "492"]);

function build({ W, H, bounds, beachhead, south, dest, crossings, out, title, routes }) {
  const proj = geoConicConformal().parallels([40, 50]).rotate([-11, 0]);
  const frame = { type: "Feature", geometry: { type: "Polygon", coordinates: [[
    [bounds[0], bounds[1]], [bounds[0], bounds[3]], [bounds[2], bounds[3]], [bounds[2], bounds[1]], [bounds[0], bounds[1]]]] } };
  proj.fitExtent([[20, 20], [W - 20, H - 20]], frame);
  proj.clipExtent([[0, 0], [W, H]]);
  const path = geoPath(proj).digits(1);
  const near = f => { const [[x0, y0], [x1, y1]] = geoBounds(f);
    return !(x1 < bounds[0] - 4 || x0 > bounds[2] + 4 || y1 < bounds[1] - 4 || y0 > bounds[3] + 4); };
  const P = (lon, lat) => proj([lon, lat]).map(v => +v.toFixed(1));

  const land = countries.features.filter(near).map(f => {
    const id = String(f.id).padStart(3, "0");
    const cls = FOCUS.has(id) ? "f" : NEAR.has(id) ? "n" : "o";
    const d = path(f);
    return d ? `<path class="${cls}" d="${d}"/>` : "";
  }).join("");

  // smooth route through waypoints (Catmull-Rom -> cubic Bezier)
  const curve = pts => {
    if (pts.length < 2) return "";
    let d = `M${pts[0][0]},${pts[0][1]}`;
    for (let i = 0; i < pts.length - 1; i++) {
      const p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2;
      const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
      const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
      d += ` C${c1[0].toFixed(1)},${c1[1].toFixed(1)} ${c2[0].toFixed(1)},${c2[1].toFixed(1)} ${p2[0]},${p2[1]}`;
    }
    return d;
  };
  const routeSvg = lanes.filter(l => routes.includes(l.id))
    .map(l => `<path class="rt" d="${curve(l.waypoints.map(w => P(w[2], w[1])))}"/>`).join("");

  const tri = (x, y, s = 13) => `<path class="tri" d="M${x},${(y - s * 0.62).toFixed(1)} L${(x + s * 0.58).toFixed(1)},${(y + s * 0.38).toFixed(1)} L${(x - s * 0.58).toFixed(1)},${(y + s * 0.38).toFixed(1)} Z"/>`;
  const label = (x, y, text, cls, dx = 9, dy = 4, anchor = "start") =>
    `<text class="${cls}" x="${x + dx}" y="${y + dy}" text-anchor="${anchor}">${text}</text>`;

  const crossSvg = crossings.map(([id, name, dx, dy, anchor]) => {
    const c = chokes[id]; const [x, y] = P(c.lon, c.lat);
    return tri(x, y) + label(x, y, name, "cx", dx ?? 10, dy ?? -6, anchor);
  }).join("");
  const dot = (x, y, cls, r) => `<circle class="${cls}" cx="${x}" cy="${y}" r="${r}"/>`;
  const beachSvg = beachhead.map(([name, lat, lon, dx, dy, anchor]) => { const [x, y] = P(lon, lat); return dot(x, y, "bh", 5.2) + label(x, y, name, "bl", dx, dy, anchor); }).join("");
  const southSvg = south.map(([name, lat, lon, dx, dy, anchor]) => { const [x, y] = P(lon, lat); return dot(x, y, "sh", 4.4) + label(x, y, name, "sl", dx, dy, anchor); }).join("");
  const destSvg = dest.map(([name, lat, lon, dx, dy, anchor]) => { const [x, y] = P(lon, lat); return dot(x, y, "ds", 3.6) + label(x, y, name, "dl", dx, dy, anchor); }).join("");

  // small truck in the deck's manner, on the Brenner route
  const [tx, ty] = P(11.45, 47.62);
  const truck = `<g transform="translate(${tx - 26},${ty - 30}) rotate(-8)">
    <rect x="0" y="4" width="34" height="15" rx="1.5" fill="url(#htDark)" stroke="${PAL.ink}" stroke-width="1.4"/>
    <path d="M34 8 h8 l5 6 v5 h-13 z" fill="${PAL.paper}" stroke="${PAL.ink}" stroke-width="1.4"/>
    <circle cx="8" cy="21" r="2.6" fill="${PAL.ink}"/><circle cx="26" cy="21" r="2.6" fill="${PAL.ink}"/><circle cx="41" cy="21" r="2.6" fill="${PAL.ink}"/></g>`;

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="${title}">
<defs>
  <pattern id="htLight" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><circle cx="2.5" cy="2.5" r="1.05" fill="${PAL.tealLight}"/></pattern>
  <pattern id="htFocus" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><circle cx="2.5" cy="2.5" r="1.45" fill="${PAL.teal}"/></pattern>
  <pattern id="htDark" width="3.4" height="3.4" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><circle cx="1.7" cy="1.7" r="1.2" fill="${PAL.teal}"/></pattern>
  <radialGradient id="fadeG" cx="50%" cy="50%" r="62%"><stop offset="72%" stop-color="#fff"/><stop offset="100%" stop-color="#000"/></radialGradient>
  <mask id="fade"><rect width="100%" height="100%" fill="url(#fadeG)"/></mask>
  <filter id="rough" x="-2%" y="-2%" width="104%" height="104%"><feTurbulence type="fractalNoise" baseFrequency="1.2" numOctaves="1" seed="3"/><feDisplacementMap in="SourceGraphic" scale="1.4"/></filter>
</defs>
<style>
  .o{fill:url(#htLight);opacity:.35;stroke:none}
  .n{fill:url(#htLight);opacity:.7;stroke:${PAL.paper};stroke-width:.8}
  .f{fill:url(#htFocus);opacity:.78;stroke:${PAL.paper};stroke-width:1.1}
  .rt{fill:none;stroke:${PAL.ink};stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
  .tri{fill:${PAL.paper};stroke:${PAL.red};stroke-width:2.6;stroke-linejoin:round}
  .bh{fill:${PAL.red};stroke:${PAL.paper};stroke-width:1.6}
  .sh{fill:${PAL.paper};stroke:${PAL.red};stroke-width:2.2}
  .ds{fill:${PAL.ink}}
  text{font-family:Inter,-apple-system,BlinkMacSystemFont,"Helvetica Neue",Arial,sans-serif;paint-order:stroke;stroke:${PAL.paper};stroke-width:3.2px;stroke-linejoin:round}
  .bl{font-size:12.5px;font-weight:650;fill:${PAL.red}}
  .sl{font-size:12px;font-weight:600;fill:${PAL.red}}
  .dl{font-size:12px;font-weight:500;fill:${PAL.ink}}
  .cx{font-size:11px;font-weight:600;fill:${PAL.ink};letter-spacing:.02em}
</style>
<g mask="url(#fade)"><g filter="url(#rough)">${land}</g></g>
<g>${routeSvg}</g>
${truck}
<g>${crossSvg}</g>
<g>${destSvg}</g>
<g>${southSvg}</g>
<g>${beachSvg}</g>
</svg>`;
  writeFileSync(resolve(root, out), svg);
  console.log("wrote", out, (svg.length / 1024).toFixed(0) + " KB");
}

// 1) beachhead map: Northern Italy and the Alpine crossings
build({
  W: 900, H: 640, out: "site/assets/img/audience-map.svg",
  title: "Map: zhol's starting provinces in Northern Italy, the Alpine crossings and the main lanes to Germany, Austria, Switzerland and France",
  bounds: [5.2, 44.0, 16.9, 49.0],
  routes: ["MIL-MUC-BRENNER", "MUC-VR-BRENNER", "MIL-STR-GOTTHARD", "MIL-LYO-FREJUS", "MIL-LYO-MONTBLANC", "PD-VIE-TARVISIO", "MIL-MUC-SWISS", "VR-MUC-TAUERN"],
  beachhead: [
    ["Milano", 45.4642, 9.19, -9, 16, "end"], ["Bergamo", 45.6983, 9.6773, 8, -6], ["Brescia", 45.5416, 10.2118, -2, -9, "end"],
    ["Verona", 45.4384, 10.9916, 8, 16], ["Trento", 46.0748, 11.1217, -9, 4, "end"], ["Bolzano", 46.4983, 11.3548, -9, 4, "end"],
    ["Vicenza", 45.5455, 11.5354, -2, -9, "end"], ["Padova", 45.4064, 11.8768, 9, 14], ["Treviso", 45.6669, 12.243, 9, -3],
    ["Modena", 44.6471, 10.9252, 9, 4], ["Torino", 45.0703, 7.6869, -9, 14, "end"], ["Cuneo", 44.3845, 7.5427, 9, 4]],
  south: [],
  dest: [["München", 48.1351, 11.582, 8, -5], ["Stuttgart", 48.7758, 9.1829, 8, -5], ["Lyon", 45.764, 4.8357, 8, 4],
         ["Wien", 48.2082, 16.3738, -8, -7, "end"], ["Zürich", 47.3769, 8.5417, -8, -7, "end"]],
  crossings: [["brenner", "Brenner", 11, 0], ["kufstein", "Kufstein", 11, -1], ["gotthard", "Gotthard", -11, -2, "end"], ["frejus", "Fréjus", -11, 8, "end"], ["montblanc", "Mont Blanc", -11, -4, "end"],
              ["tarvisio", "Tarvisio", 11, 4], ["san_bernardino", "S. Bernardino", 11, 8]],
});

// 2) whole-Italy map with the South–North segment
build({
  W: 640, H: 860, out: "site/assets/img/segments-map.svg",
  title: "Map: the two Italian segments: Alpine-lane hauliers in the north and South–North long-haul from Sicily and Campania",
  bounds: [6.0, 36.4, 16.5, 48.4],
  routes: ["VIT-MIL", "CT-MUC", "MIL-MUC-BRENNER", "MIL-LYO-FREJUS"],
  beachhead: [["Milano", 45.4642, 9.19, -9, 4, "end"], ["Verona", 45.4384, 10.9916, 9, 4], ["Torino", 45.0703, 7.6869, -9, 14, "end"], ["Trento", 46.0748, 11.1217, 9, 4]],
  south: [["Vittoria", 36.9536, 14.5326, -9, 4, "end"], ["Catania", 37.5079, 15.083, 9, 4], ["Salerno", 40.6824, 14.7681, 9, 4], ["Napoli", 40.8518, 14.2681, -9, -4, "end"]],
  dest: [["München", 48.1351, 11.582, 8, -5], ["Lyon", 45.764, 4.8357, 6, 16]],
  crossings: [["brenner", "Brenner", 11, 0], ["frejus", "Fréjus", 11, -4], ["messina_strait", "Stretto di Messina", -12, -6, "end"]],
});
