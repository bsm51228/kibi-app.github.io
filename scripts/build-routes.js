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

const ROOT = path.resolve(__dirname, '..');
const ROUTES_DIR = path.join(ROOT, 'routes');
const TEMPLATE_PATH = path.join(ROUTES_DIR, '_template.html');
const SITEMAP_PATH = path.join(ROOT, 'sitemap.xml');
const TODAY = new Date().toISOString().split('T')[0];

// ── Helpers ─────────────────────────────────────────────────────────────────

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function formatStopType(stopType) {
  switch (stopType) {
    case 'service_plaza': return { label: 'Service Plaza', cssClass: 'type-badge type-badge--plaza' };
    case 'rest_area':     return { label: 'Rest Area',     cssClass: 'type-badge type-badge--rest' };
    default:              return { label: 'Exit',          cssClass: 'type-badge' };
  }
}

function buildExitRow(exit) {
  const num = exit.exit_number || '\u2014';
  const name = escapeHtml(exit.exit_name || 'Highway Exit');
  const state = escapeHtml(exit.state || '');
  const type = formatStopType(exit.stop_type);
  const coords = `${exit.lat.toFixed(4)}, ${exit.lng.toFixed(4)}`;

  return `        <tr>
          <td class="exit-num">${escapeHtml(num)}</td>
          <td class="exit-name">${name}</td>
          <td class="exit-state">${state}</td>
          <td><span class="${type.cssClass}">${type.label}</span></td>
          <td class="exit-coords">${coords}</td>
        </tr>`;
}

// ── Build route HTML pages ──────────────────────────────────────────────────

function buildRoutePages() {
  const template = fs.readFileSync(TEMPLATE_PATH, 'utf8');
  const jsonFiles = fs.readdirSync(ROUTES_DIR)
    .filter(f => f.endsWith('.json'))
    .sort();

  const routes = [];

  for (const jsonFile of jsonFiles) {
    const data = JSON.parse(fs.readFileSync(path.join(ROUTES_DIR, jsonFile), 'utf8'));
    routes.push(data);

    const exitRows = data.exits.map(buildExitRow).join('\n');

    let html = template
      .replace(/\{\{ORIGIN\}\}/g, escapeHtml(data.origin))
      .replace(/\{\{DESTINATION\}\}/g, escapeHtml(data.destination))
      .replace(/\{\{HIGHWAY\}\}/g, escapeHtml(data.highway))
      .replace(/\{\{SLUG\}\}/g, escapeHtml(data.route_slug))
      .replace(/\{\{EXIT_COUNT\}\}/g, String(data.exit_count))
      .replace(/\{\{MILES\}\}/g, String(data.miles))
      .replace(/\{\{EXIT_ROWS\}\}/g, exitRows);

    const outPath = path.join(ROUTES_DIR, `${data.route_slug}.html`);
    fs.writeFileSync(outPath, html);
    console.log(`  ✓ ${data.route_slug}.html (${data.exit_count} exits, ~${data.miles} mi)`);
  }

  return routes;
}

// ── Build routes/index.html ─────────────────────────────────────────────────

function buildIndexPage(routes) {
  // Read the existing index to preserve the full page structure.
  // We only regenerate the route cards and structured data.
  const sorted = [...routes].sort((a, b) =>
    `${a.origin} ${a.destination}`.localeCompare(`${b.origin} ${b.destination}`)
  );

  const cards = sorted.map(r => {
    const hw = escapeHtml(r.highway.split(',')[0].trim());
    return `      <a href="${r.route_slug}.html" class="route-card">
        <span class="route-card-hw">${hw}</span>
        <h3>${escapeHtml(r.origin)} &rarr; ${escapeHtml(r.destination)}</h3>
        <p class="route-card-meta">${r.exit_count} exits scored &middot; ~${r.miles} mi</p>
        <span class="route-card-arrow">View stops &rarr;</span>
      </a>`;
  }).join('\n');

  const listItems = sorted.map((r, i) =>
    `          {"@type": "ListItem", "position": ${i + 1}, "name": "${r.origin} to ${r.destination}", "url": "https://drivekibi.com/routes/${r.route_slug}.html"}`
  ).join(',\n');

  // Read existing index and replace the dynamic sections
  let indexHtml = fs.readFileSync(path.join(ROUTES_DIR, 'index.html'), 'utf8');

  // Replace route cards
  indexHtml = indexHtml.replace(
    /(<div class="routes-grid">)[\s\S]*?(<\/div>\s*<\/section>)/,
    `$1\n${cards}\n    </div>\n  </section>`
  );

  // Replace numberOfItems
  indexHtml = indexHtml.replace(
    /"numberOfItems":\s*\d+/,
    `"numberOfItems": ${sorted.length}`
  );

  // Replace itemListElement
  indexHtml = indexHtml.replace(
    /"itemListElement":\s*\[[\s\S]*?\]/,
    `"itemListElement": [\n${listItems}\n        ]`
  );

  fs.writeFileSync(path.join(ROUTES_DIR, 'index.html'), indexHtml);
  console.log(`  ✓ index.html (${sorted.length} route cards)`);
}

// ── Update sitemap.xml ──────────────────────────────────────────────────────

function updateSitemap(routes) {
  let sitemap = fs.readFileSync(SITEMAP_PATH, 'utf8');

  // Remove existing route entries (everything after the comment)
  sitemap = sitemap.replace(
    /\n\s*<!-- Route guide pages -->[\s\S]*?(<\/urlset>)/,
    '\n$1'
  );

  // Build new route entries
  const routeEntries = [
    // Index page
    `  <!-- Route guide pages -->
  <url>
    <loc>https://drivekibi.com/routes/index.html</loc>
    <lastmod>${TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>`
  ];

  const sorted = [...routes].sort((a, b) => a.route_slug.localeCompare(b.route_slug));
  for (const r of sorted) {
    routeEntries.push(`  <url>
    <loc>https://drivekibi.com/routes/${r.route_slug}.html</loc>
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
  console.log(`  ✓ sitemap.xml (${routes.length + 1} route URLs)`);
}

// ── Main ────────────────────────────────────────────────────────────────────

console.log('Building route pages...\n');

const routes = buildRoutePages();
console.log('');
buildIndexPage(routes);
updateSitemap(routes);

console.log(`\nDone. ${routes.length} route pages generated.`);
