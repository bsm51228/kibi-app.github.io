#!/usr/bin/env node
/**
 * build-routes.js — Generate route HTML pages from JSON data + template.
 *
 * Reads each *.json file in routes/, applies routes/_template.html,
 * writes the HTML page, regenerates routes/index.html, and updates sitemap.xml.
 *
 * Usage:
 *   node scripts/build-routes.js
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const ROUTES_DIR = path.join(ROOT, 'routes');
const TEMPLATE_PATH = path.join(ROUTES_DIR, '_template.html');
const SITEMAP_PATH = path.join(ROOT, 'sitemap.xml');
const TODAY = new Date().toISOString().split('T')[0];

// ── Helpers ─────────────────────────────────────────────────────────────────

function escapeHtml(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function formatStopType(stopType) {
  switch (stopType) {
    case 'service_plaza': return { label: 'Service Plaza', cssClass: 'type-badge type-badge--plaza' };
    case 'rest_area':     return { label: 'Rest Area',     cssClass: 'type-badge type-badge--rest' };
    default:              return { label: 'Exit',          cssClass: 'type-badge' };
  }
}

function poiIcon(types) {
  if (types.includes('gas')) return '\u26FD';
  if (types.includes('coffee')) return '\u2615';
  if (types.includes('food')) return '\uD83C\uDF54';
  if (types.includes('convenience')) return '\uD83C\uDFEA';
  return '\uD83D\uDCCD';
}

function buildPoiChips(places) {
  if (!places || places.length === 0) return '<span style="color:var(--text-muted);font-size:.75rem;">\u2014</span>';

  const chips = places.slice(0, 4).map(p => {
    const icon = poiIcon(p.types || []);
    const rating = p.rating ? `<span class="poi-rating">${p.rating.toFixed(1)}\u2605</span>` : '';
    return `<span class="poi-chip"><span class="poi-icon">${icon}</span>${escapeHtml(p.name)}${rating ? ' ' + rating : ''}</span>`;
  });

  return `<div class="poi-list">${chips.join('')}</div>`;
}

function buildExitRow(exit) {
  const num = exit.exit_number || '\u2014';
  const name = escapeHtml(exit.exit_name || 'Highway Exit');
  const state = escapeHtml(exit.state || '');
  const type = formatStopType(exit.stop_type);
  const coords = `${exit.lat.toFixed(4)}, ${exit.lng.toFixed(4)}`;
  const pois = buildPoiChips(exit.places);

  return `        <tr>
          <td class="exit-num" data-label="Exit">${escapeHtml(num)}</td>
          <td class="exit-name" data-label="Location">${name}</td>
          <td class="exit-state" data-label="State">${state}</td>
          <td data-label="Type"><span class="${type.cssClass}">${type.label}</span></td>
          <td data-label="What's Here">${pois}</td>
          <td class="exit-coords" data-label="Coordinates">${coords}</td>
        </tr>`;
}

// ── Date helpers ────────────────────────────────────────────────────────────

function getJsonMtime(jsonPath) {
  return fs.statSync(jsonPath).mtime.toISOString().split('T')[0];
}

// First-commit ISO date for a file from git log. Falls back to mtime if git
// is unavailable or the file is untracked.
// Performance: ~50ms per file via shell-out. At 100+ routes, add a cache at
// scripts/.published-dates-cache.json keyed by file path so this runs once
// per file lifetime instead of once per build.
function getFirstCommitDate(jsonPath) {
  try {
    const rel = path.relative(ROOT, jsonPath);
    const out = execSync(
      `git log --diff-filter=A --follow --format=%aI -- "${rel}" | tail -1`,
      { cwd: ROOT, encoding: 'utf8' }
    ).trim();
    if (out) return out.split('T')[0];
  } catch (_) { /* fall through */ }
  return getJsonMtime(jsonPath);
}

// ── Derivations ─────────────────────────────────────────────────────────────

function formatDriveHours(miles) {
  const totalMin = Math.round((miles / 65) * 60);
  const h = Math.floor(totalMin / 60);
  const m = totalMin % 60;
  return m === 0 ? `${h}h` : `${h}h ${m}m`;
}

function uniqueStates(exits) {
  return [...new Set(exits.map(e => e.state).filter(Boolean))];
}

function buildStatesTraversed(exits) {
  const s = uniqueStates(exits);
  if (s.length === 0) return 'multiple states';
  if (s.length === 1) return s[0];
  if (s.length === 2) return `${s[0]} and ${s[1]}`;
  return s.slice(0, -1).join(', ') + ', and ' + s[s.length - 1];
}

function extractCityState(address) {
  // "1429 W Walnut Ave, Dalton, GA 30720, USA" → "Dalton, GA"
  const parts = address.split(',').map(s => s.trim());
  if (parts.length < 3) return parts[0] || '';
  const city = parts[parts.length - 3];
  const state = (parts[parts.length - 2] || '').split(' ')[0];
  return state ? `${city}, ${state}` : city;
}

function buildTopExitsSummary(data) {
  const top = data.exits.slice(0, 3);
  if (top.length === 0) return 'No scored stops on this route yet.';
  const phrases = top.map(e => {
    const cs = (e.places && e.places[0] && e.places[0].address)
      ? extractCityState(e.places[0].address)
      : `Exit ${e.exit_number || ''}`.trim();
    return `${cs} (Exit ${e.exit_number || '\u2014'})`;
  });
  return `Top stops on this route include ${phrases.join(', ')}.`;
}

function countRestAreas(exits) {
  return exits.filter(e =>
    e.stop_type === 'rest_area' || e.stop_type === 'service_plaza'
  ).length;
}

// ── Single-sentence fallbacks ───────────────────────────────────────────────
// Used only when JSON omits the hand-written field. Per project convention,
// missing narrative content surfaces as "fewer words on page" — never as
// auto-generated paragraphs.

function fallbackNarrative(data) {
  return `${data.miles}-mile drive on ${data.highway} between ${data.origin} and ${data.destination}.`;
}
function fallbackTips(data) {
  const hw = data.highway.split(',')[0].trim();
  return `${data.exit_count} stops scored along ${hw}; see the table above for details.`;
}
function fallbackEv(_data) {
  return `Charging information for this route is being researched.`;
}

// ── FAQ generation ──────────────────────────────────────────────────────────

function buildFaqItems(data) {
  const driveHours = formatDriveHours(data.miles);
  const states     = buildStatesTraversed(data.exits);
  const topSummary = data.top_exits_summary || buildTopExitsSummary(data);
  const restCount  = countRestAreas(data.exits);
  const totalExits = data.exit_count;
  const regular    = totalExits - restCount;

  // Q5 — rest areas
  const restAreaAns = restCount > 0
    ? `Yes — this guide includes ${restCount} rest area${restCount === 1 ? '' : 's'} or service plaza${restCount === 1 ? '' : 's'} along ${data.highway}, plus ${regular} regular exit${regular === 1 ? '' : 's'} scored for stops.`
    : `This route has no scored rest areas in our guide; all ${totalExits} stops are regular highway exits with food, gas, and restrooms.`;

  // Q6 — tolls (4-case logic)
  let tollsAns;
  if (data.has_tolls === true && data.tolls_summary) {
    tollsAns = `Yes — ${data.tolls_summary}.`;
  } else if (data.has_tolls === true) {
    tollsAns = `Yes — this route has tolls. Check your navigation app for current estimates.`;
  } else if (data.has_tolls === false) {
    tollsAns = `No — this is a toll-free drive.`;
  } else {
    tollsAns = `Toll information varies — check your navigation app for current toll estimates.`;
  }

  return [
    { q: `How long does it take to drive from ${data.origin} to ${data.destination}?`,
      a: `About ${data.miles} miles, which takes roughly ${driveHours} at typical highway speeds. Add 30–60 minutes for fuel and food stops.` },
    { q: `What's the best route from ${data.origin} to ${data.destination}?`,
      a: `Most drivers take ${data.highway}. The drive crosses ${states}, covering ${data.miles} miles.` },
    { q: `Where are the best places to stop between ${data.origin} and ${data.destination}?`,
      a: topSummary },
    { q: `Are there rest areas on the ${data.origin} to ${data.destination} drive?`,
      a: restAreaAns },
    { q: `Are there tolls on the drive from ${data.origin} to ${data.destination}?`,
      a: tollsAns }
  ];
}

function buildFaqHtml(data) {
  return buildFaqItems(data).map(item =>
`        <details>
          <summary>${escapeHtml(item.q)}</summary>
          <p>${escapeHtml(item.a)}</p>
        </details>`
  ).join('\n');
}

function buildFaqJsonld(data) {
  const items = buildFaqItems(data).map(item => ({
    "@type": "Question",
    "name":  item.q,
    "acceptedAnswer": { "@type": "Answer", "text": item.a }
  }));
  return JSON.stringify(items, null, 2).replace(/<\//g, '<\\/');
}

// ── Related routes ──────────────────────────────────────────────────────────

function buildRelatedRoutes(current, allRoutes) {
  const currentHw = new Set(current.highway.split(',').map(s => s.trim()));
  const scored = allRoutes
    .filter(r => r.route_slug !== current.route_slug)
    .map(r => {
      let score = 0;
      for (const hw of r.highway.split(',').map(s => s.trim())) {
        if (currentHw.has(hw)) score += 3;
      }
      if (r.origin === current.origin || r.destination === current.destination) score += 2;
      if (r.origin === current.destination || r.destination === current.origin) score += 1;
      return { r, score };
    })
    .sort((a, b) => b.score - a.score)
    .slice(0, 3);

  if (scored.length === 0) {
    return '      <p style="color:var(--text-muted);font-size:.9rem;">More routes coming soon.</p>';
  }
  return scored.map(({ r }) => {
    const hw = escapeHtml(r.highway.split(',')[0].trim());
    return `      <a href="${r.route_slug}" class="related-card">
        <span class="related-card-hw">${hw}</span>
        <h3>${escapeHtml(r.origin)} &rarr; ${escapeHtml(r.destination)}</h3>
        <p>${r.exit_count} exits &middot; ~${r.miles} mi</p>
      </a>`;
  }).join('\n');
}

// ── Build route HTML pages ──────────────────────────────────────────────────

function buildRoutePages() {
  const template = fs.readFileSync(TEMPLATE_PATH, 'utf8');
  const jsonFiles = fs.readdirSync(ROUTES_DIR)
    .filter(f => f.endsWith('.json'))
    .sort();

  // First pass: load all routes (needed for related-routes scoring).
  const allRoutes = jsonFiles.map(f =>
    JSON.parse(fs.readFileSync(path.join(ROUTES_DIR, f), 'utf8'))
  );

  for (let i = 0; i < jsonFiles.length; i++) {
    const jsonFile = jsonFiles[i];
    const data = allRoutes[i];
    const jsonPath = path.join(ROUTES_DIR, jsonFile);

    const exitRows         = data.exits.map(buildExitRow).join('\n');
    const driveHours       = formatDriveHours(data.miles);
    const stateCount       = uniqueStates(data.exits).length;
    const highwayPrimary   = data.highway.split(',')[0].trim();
    const updatedDate      = getJsonMtime(jsonPath);
    const publishedDate    = getFirstCommitDate(jsonPath);
    const routeNarrative   = data.route_narrative   || fallbackNarrative(data);
    const tipsNarrative    = data.tips_narrative    || fallbackTips(data);
    const evNarrative      = data.ev_narrative      || fallbackEv(data);
    const topExitsSummary  = data.top_exits_summary || buildTopExitsSummary(data);
    const faqHtml          = buildFaqHtml(data);
    const faqJsonld        = buildFaqJsonld(data);
    const relatedRoutesHtml = buildRelatedRoutes(data, allRoutes);

    let html = template
      .replace(/\{\{ORIGIN\}\}/g, escapeHtml(data.origin))
      .replace(/\{\{DESTINATION\}\}/g, escapeHtml(data.destination))
      .replace(/\{\{HIGHWAY\}\}/g, escapeHtml(data.highway))
      .replace(/\{\{HIGHWAY_PRIMARY\}\}/g, escapeHtml(highwayPrimary))
      .replace(/\{\{SLUG\}\}/g, escapeHtml(data.route_slug))
      .replace(/\{\{EXIT_COUNT\}\}/g, String(data.exit_count))
      .replace(/\{\{MILES\}\}/g, String(data.miles))
      .replace(/\{\{DRIVE_HOURS\}\}/g, escapeHtml(driveHours))
      .replace(/\{\{STATE_COUNT\}\}/g, String(stateCount))
      .replace(/\{\{ROUTE_NARRATIVE\}\}/g, escapeHtml(routeNarrative))
      .replace(/\{\{TIPS_NARRATIVE\}\}/g, escapeHtml(tipsNarrative))
      .replace(/\{\{EV_NARRATIVE\}\}/g, escapeHtml(evNarrative))
      .replace(/\{\{TOP_EXITS_SUMMARY\}\}/g, escapeHtml(topExitsSummary))
      .replace(/\{\{FAQ_HTML\}\}/g, faqHtml)
      .replace(/\{\{FAQ_JSONLD\}\}/g, faqJsonld)
      .replace(/\{\{RELATED_ROUTES_HTML\}\}/g, relatedRoutesHtml)
      .replace(/\{\{PUBLISHED_DATE\}\}/g, publishedDate)
      .replace(/\{\{UPDATED_DATE\}\}/g, updatedDate)
      .replace(/\{\{EXIT_ROWS\}\}/g, exitRows);

    // Routes with no scored exits get noindex (follow stays — let
    // PageRank flow through internal links). Sitemap also excludes
    // these — see updateSitemap().
    if (data.exit_count === 0) {
      html = html.replace(
        /<meta name="robots" content="index, follow" \/>/,
        '<meta name="robots" content="noindex, follow" />'
      );
    }

    const outPath = path.join(ROUTES_DIR, `${data.route_slug}.html`);
    fs.writeFileSync(outPath, html);
    const noindexFlag = data.exit_count === 0 ? ' [noindex]' : '';
    console.log(`  ✓ ${data.route_slug}.html (${data.exit_count} exits, ~${data.miles} mi)${noindexFlag}`);
  }

  return allRoutes;
}

// ── Build routes/index.html ─────────────────────────────────────────────────

function buildIndexPage(routes) {
  // Same empty-exit filter as updateSitemap(): hide cards for routes
  // with no scored exits. Detail pages still exist (noindex, follow)
  // so external/related-routes links keep working. Cards auto-appear
  // when exits get populated.
  const indexable = routes.filter(r => r.exit_count > 0);
  const sorted = [...indexable].sort((a, b) =>
    `${a.origin} ${a.destination}`.localeCompare(`${b.origin} ${b.destination}`)
  );

  const cards = sorted.map(r => {
    const hw = escapeHtml(r.highway.split(',')[0].trim());
    return `      <a href="${r.route_slug}" class="route-card">
        <span class="route-card-hw">${hw}</span>
        <h3>${escapeHtml(r.origin)} &rarr; ${escapeHtml(r.destination)}</h3>
        <p class="route-card-meta">${r.exit_count} exits scored &middot; ~${r.miles} mi</p>
        <span class="route-card-arrow">View stops &rarr;</span>
      </a>`;
  }).join('\n');

  const listItems = sorted.map((r, i) =>
    `          {"@type": "ListItem", "position": ${i + 1}, "name": "${r.origin} to ${r.destination}", "url": "https://drivekibi.com/routes/${r.route_slug}"}`
  ).join(',\n');

  let indexHtml = fs.readFileSync(path.join(ROUTES_DIR, 'index.html'), 'utf8');

  indexHtml = indexHtml.replace(
    /(<div class="routes-grid">)[\s\S]*?(<\/div>\s*<\/section>)/,
    `$1\n${cards}\n    </div>\n  </section>`
  );

  indexHtml = indexHtml.replace(
    /"numberOfItems":\s*\d+/,
    `"numberOfItems": ${sorted.length}`
  );

  indexHtml = indexHtml.replace(
    /"itemListElement":\s*\[[\s\S]*?\]/,
    `"itemListElement": [\n${listItems}\n        ]`
  );

  fs.writeFileSync(path.join(ROUTES_DIR, 'index.html'), indexHtml);
  const skipped = routes.length - indexable.length;
  const skipNote = skipped > 0 ? ` (${skipped} empty-exit routes excluded)` : '';
  console.log(`  ✓ index.html (${sorted.length} route cards)${skipNote}`);
}

// ── Update sitemap.xml ──────────────────────────────────────────────────────

function updateSitemap(routes) {
  let sitemap = fs.readFileSync(SITEMAP_PATH, 'utf8');

  sitemap = sitemap.replace(
    /\n\s*<!-- Route guide pages -->[\s\S]*?(<\/urlset>)/,
    '\n$1'
  );

  const routeEntries = [
    `  <!-- Route guide pages -->
  <url>
    <loc>https://drivekibi.com/routes/</loc>
    <lastmod>${TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>`
  ];

  // Skip routes with no scored exits — they're noindex'd, so excluding
  // them stops Google from being told to crawl them.
  const indexable = routes.filter(r => r.exit_count > 0);
  const sorted = [...indexable].sort((a, b) => a.route_slug.localeCompare(b.route_slug));
  for (const r of sorted) {
    routeEntries.push(`  <url>
    <loc>https://drivekibi.com/routes/${r.route_slug}</loc>
    <lastmod>${TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>`);
  }

  sitemap = sitemap.replace(
    '</urlset>',
    routeEntries.join('\n') + '\n</urlset>\n'
  );

  fs.writeFileSync(SITEMAP_PATH, sitemap);
  const skipped = routes.length - indexable.length;
  const skipNote = skipped > 0 ? ` (${skipped} empty-exit routes excluded)` : '';
  console.log(`  ✓ sitemap.xml (${indexable.length + 1} route URLs)${skipNote}`);
}

// ── Main ────────────────────────────────────────────────────────────────────

console.log('Building route pages...\n');

const routes = buildRoutePages();
console.log('');
buildIndexPage(routes);
updateSitemap(routes);

console.log(`\nDone. ${routes.length} route pages generated.`);
