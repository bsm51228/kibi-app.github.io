#!/usr/bin/env python3
"""
build_route_pages.py
Reads routes/*.json and generates:
  - routes/<slug>.html  (one per route)
  - routes/index.html   (hub listing all routes)
Design system matches index.html exactly (Lora + system-ui, 9 CSS variables).
"""

import os
import json
import glob

ROUTES_DIR = "routes"

TYPE_LABELS = {
    "rest_area":         "Rest Area",
    "service_plaza":     "Service Plaza",
    "exit_ramp":         "Exit",
    "motorway_junction": "Junction",
}


def type_label(stop_type):
    if not stop_type:
        return "Exit"
    return TYPE_LABELS.get(stop_type.strip(), "Exit")


# ── Shared CSS ────────────────────────────────────────────────────────────────

SHARED_CSS = """
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }

    :root {
      --green:          #2EBD7A;
      --bg:             #060F0B;
      --surface:        #0A1A12;
      --surface-mid:    #0D1F17;
      --border-subtle:  rgba(46,189,122,0.08);
      --border-active:  rgba(46,189,122,0.25);
      --text-primary:   #E8F0EC;
      --text-secondary: #C8DDD4;
      --text-muted:     rgba(255,255,255,0.45);
    }

    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: var(--bg);
      color: var(--text-primary);
      min-width: 320px;
    }

    h1, h2, h3 { font-family: 'Lora', Georgia, serif; }

    /* ── NAV ── */
    nav#main-nav {
      position: sticky;
      top: 0;
      z-index: 100;
      background: rgba(6,15,11,0.95);
      -webkit-backdrop-filter: blur(14px);
      backdrop-filter: blur(14px);
      border-bottom: 1px solid var(--border-subtle);
      height: 64px;
      padding: 0 56px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .nav-logo { display: inline-flex; align-items: center; text-decoration: none; }
    .nav-right { display: flex; align-items: center; gap: 8px; }
    .nav-how {
      font-size: 14px; color: var(--text-muted);
      text-decoration: none; margin-right: 20px;
      transition: color 0.2s;
    }
    .nav-how:hover { color: var(--text-primary); }
    .nav-cta {
      background: var(--green); color: #060F0B;
      font-weight: 700; font-size: 14px;
      padding: 10px 22px; border-radius: 99px;
      text-decoration: none; display: inline-block;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .nav-cta:hover {
      transform: translateY(-1px);
      box-shadow: 0 8px 24px rgba(46,189,122,0.35);
    }
    .hamburger {
      display: none; flex-direction: column;
      justify-content: center; gap: 5px;
      width: 44px; height: 44px;
      background: none; border: none;
      cursor: pointer; padding: 8px;
    }
    .hamburger span {
      display: block; width: 22px; height: 2px;
      background: var(--text-primary); border-radius: 2px;
      transition: transform 0.3s, opacity 0.3s;
      transform-origin: center;
    }
    .hamburger.open span:nth-child(1) { transform: translateY(7px) rotate(45deg); }
    .hamburger.open span:nth-child(2) { opacity: 0; }
    .hamburger.open span:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }
    .nav-drawer {
      display: none; position: fixed; inset: 0; z-index: 99;
      background: rgba(6,15,11,0.97);
      -webkit-backdrop-filter: blur(20px);
      backdrop-filter: blur(20px);
      flex-direction: column; align-items: center;
      justify-content: center; gap: 20px;
      opacity: 0; pointer-events: none;
      transition: opacity 0.25s;
    }
    .nav-drawer.open { opacity: 1; pointer-events: all; }
    .nav-drawer a {
      font-family: 'Lora', serif; font-size: 24px; font-weight: 700;
      color: var(--text-primary); text-decoration: none; text-align: center;
      transition: color 0.2s;
    }
    .nav-drawer a:hover { color: var(--green); }
    .nav-drawer .nav-cta-drawer {
      background: var(--green); color: #060F0B;
      padding: 14px 36px; border-radius: 14px; font-size: 18px;
    }

    /* ── HERO ── */
    .route-hero {
      background: var(--surface);
      border-bottom: 1px solid var(--border-subtle);
      padding: 80px 80px 64px;
    }
    .breadcrumb {
      font-size: .72rem; color: var(--text-muted);
      letter-spacing: .08em; margin-bottom: 24px;
      text-decoration: none;
    }
    .breadcrumb a { color: var(--text-muted); text-decoration: none; }
    .breadcrumb a:hover { color: var(--green); }
    .route-hero h1 {
      font-size: clamp(2rem, 4vw, 3rem);
      font-weight: 700; color: var(--text-primary);
      line-height: 1.1; margin-bottom: 20px;
    }
    .route-subhead {
      font-size: 1rem; font-weight: 300;
      color: var(--text-secondary); line-height: 1.7;
      max-width: 640px; margin-bottom: 28px;
    }
    .stat-pills { display: flex; gap: 12px; flex-wrap: wrap; }
    .stat-pill {
      background: rgba(46,189,122,0.1);
      border: 1px solid rgba(46,189,122,0.25);
      color: var(--green); border-radius: 100px;
      padding: 6px 16px; font-size: .78rem; font-weight: 600;
    }

    /* ── EXIT TABLE ── */
    .exit-section {
      background: var(--bg);
      padding: 64px 80px;
    }
    .section-label {
      font-family: system-ui, sans-serif;
      font-size: 11px; font-weight: 700;
      letter-spacing: 2px; color: var(--green);
      text-transform: uppercase; margin-bottom: 16px;
    }
    .exit-section h2 {
      font-size: clamp(1.5rem, 3vw, 2rem);
      font-weight: 700; color: var(--text-primary);
      margin-bottom: 36px;
    }
    .exit-table-wrap { overflow-x: auto; }
    table {
      width: 100%; border-collapse: collapse;
      font-size: .9rem;
    }
    thead tr {
      background: var(--surface);
      border-bottom: 1px solid var(--border-subtle);
    }
    thead th {
      padding: 14px 16px; text-align: left;
      font-size: .72rem; font-weight: 700;
      letter-spacing: .1em; text-transform: uppercase;
      color: var(--text-muted);
      white-space: nowrap;
    }
    tbody tr:nth-child(odd)  { background: var(--bg); }
    tbody tr:nth-child(even) { background: var(--surface-mid); }
    tbody tr { border-bottom: 1px solid var(--border-subtle); }
    tbody td { padding: 14px 16px; vertical-align: middle; }
    .exit-num {
      font-family: 'Lora', serif; font-weight: 700;
      color: var(--green); white-space: nowrap;
    }
    .exit-name {
      font-weight: 500; color: var(--text-primary);
    }
    .exit-state {
      color: var(--text-muted); font-size: .85rem;
    }
    .type-badge {
      display: inline-block;
      background: rgba(46,189,122,0.1);
      color: var(--green); border-radius: 100px;
      padding: 2px 10px; font-size: .68rem; font-weight: 600;
      white-space: nowrap;
    }
    .exit-coords {
      color: var(--text-muted); font-size: .78rem;
      font-family: 'SF Mono', 'Fira Code', monospace;
      white-space: nowrap;
    }

    /* ── CTA ── */
    .route-cta {
      background: var(--surface);
      border-top: 1px solid var(--border-subtle);
      text-align: center; padding: 80px 56px;
    }
    .route-cta h2 {
      font-size: 2rem; font-style: italic;
      color: var(--text-primary); margin-bottom: 16px;
    }
    .route-cta p {
      font-size: 1rem; font-weight: 300;
      color: var(--text-secondary); line-height: 1.7;
      max-width: 520px; margin: 0 auto 32px;
    }
    .btn-coming-soon {
      background: var(--green); color: #060F0B;
      font-weight: 700; font-size: 16px;
      padding: 16px 32px; border-radius: 14px;
      border: none; cursor: default; opacity: 0.75;
      display: inline-block;
    }
    .cta-sub {
      display: block; margin-top: 14px;
      font-size: .78rem; color: var(--text-muted);
    }

    /* ── BACK LINK ── */
    .back-link {
      text-align: center; padding: 32px;
      border-top: 1px solid var(--border-subtle);
    }
    .back-link a {
      color: var(--text-muted); font-size: .84rem;
      text-decoration: none; transition: color 0.2s;
    }
    .back-link a:hover { color: var(--text-secondary); }

    /* ── FOOTER ── */
    footer {
      background: #060F0B;
      border-top: 1px solid rgba(46,189,122,0.08);
      padding: 48px 80px;
      display: flex; justify-content: space-between;
      align-items: center; flex-wrap: wrap; gap: 16px;
    }
    .footer-left { display: flex; flex-direction: column; gap: 0; }
    .footer-brand { display: flex; align-items: center; gap: 8px; }
    .footer-tagline { font-size: 13px; color: rgba(255,255,255,0.2); display: block; margin-top: 5px; }
    .footer-privacy {
      font-size: 13px; color: rgba(255,255,255,0.2);
      margin-top: 4px; text-decoration: none; display: block;
    }
    .footer-privacy:hover { color: rgba(255,255,255,0.5); }
    .footer-links { display: flex; gap: 28px; flex-wrap: wrap; justify-content: center; }
    .footer-links a {
      font-size: 13px; color: var(--text-muted);
      text-decoration: none; transition: color 0.2s;
    }
    .footer-links a:hover { color: var(--text-secondary); }
    .footer-copy { font-size: 12px; color: var(--text-muted); flex-shrink: 0; }
    .footer-osm { font-size: .7rem; color: var(--text-muted); opacity: .5; margin-top: 8px; }
    .footer-osm a { color: inherit; }

    /* ── RESPONSIVE ── */
    @media (max-width: 960px) {
      .route-hero { padding: 64px 40px 48px; }
      .exit-section { padding: 48px 40px; }
      .route-cta { padding: 64px 40px; }
      footer { padding: 48px 40px; }
    }
    @media (max-width: 768px) {
      nav#main-nav { padding: 0 24px; }
      .nav-right .nav-how { display: none; }
      .nav-right .nav-cta { display: none; }
      .hamburger { display: flex; }
      .nav-drawer { display: flex; }
      .route-hero { padding: 48px 24px 40px; }
      .exit-section { padding: 40px 24px; }
      .route-cta { padding: 56px 24px; }
      footer { padding: 40px 24px; flex-direction: column; align-items: flex-start; }
      .stat-pills { flex-wrap: wrap; }
    }
"""

# ── Index page additional CSS ─────────────────────────────────────────────────

INDEX_EXTRA_CSS = """
    .routes-hero {
      background: var(--surface);
      border-bottom: 1px solid var(--border-subtle);
      padding: 80px 80px 64px;
      text-align: center;
    }
    .routes-hero h1 {
      font-size: clamp(2rem, 4vw, 3rem);
      font-weight: 700; color: var(--text-primary);
      line-height: 1.1; margin-bottom: 20px;
    }
    .routes-hero p {
      font-size: 1rem; font-weight: 300;
      color: var(--text-secondary); line-height: 1.7;
      max-width: 560px; margin: 0 auto;
    }
    .routes-grid-section {
      background: var(--bg); padding: 64px 80px;
    }
    .routes-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 20px;
      margin-top: 8px;
    }
    .route-card {
      background: rgba(13,31,23,0.6);
      border: 1px solid rgba(46,189,122,0.08);
      border-radius: 16px; padding: 28px 24px;
      text-decoration: none; display: block;
      transition: border-color 0.25s, background 0.25s, transform 0.2s;
    }
    .route-card:hover {
      border-color: rgba(46,189,122,0.3);
      background: rgba(13,31,23,0.85);
      transform: translateY(-3px);
    }
    .route-card-hw {
      display: inline-block;
      background: rgba(46,189,122,0.1);
      border: 1px solid rgba(46,189,122,0.25);
      color: var(--green); border-radius: 100px;
      padding: 3px 12px; font-size: .72rem; font-weight: 700;
      letter-spacing: .05em; margin-bottom: 14px;
    }
    .route-card h3 {
      font-family: 'Lora', serif; font-weight: 700;
      font-size: 1.15rem; color: var(--text-primary);
      line-height: 1.3; margin-bottom: 10px;
    }
    .route-card-meta {
      font-size: .8rem; color: var(--text-muted);
    }
    .route-card-arrow {
      display: block; margin-top: 16px;
      font-size: .82rem; color: var(--green);
      font-weight: 600;
    }
    @media (max-width: 768px) {
      .routes-hero { padding: 48px 24px 40px; }
      .routes-grid-section { padding: 40px 24px; }
      .routes-grid { grid-template-columns: 1fr; }
    }
"""

# ── Nav / Footer helpers ──────────────────────────────────────────────────────

def nav_html(prefix="../"):
    return f"""  <!-- NAV -->
  <nav id="main-nav">
    <a href="{prefix}" class="nav-logo">
      <img src="{prefix}Kibi_Logo_Horizontal_White.png" alt="Kibi" style="height:28px;display:block;" />
    </a>
    <div class="nav-right">
      <a href="{prefix}#how-it-works" class="nav-how">How It Works</a>
      <a href="index.html" class="nav-how">Route Guide</a>
      <a href="{prefix}#waitlist" class="nav-cta">Join the Waitlist →</a>
      <button class="hamburger" id="hamburger" aria-label="Open menu" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
  </nav>
  <div id="nav-drawer" class="nav-drawer" aria-hidden="true">
    <a href="{prefix}#how-it-works">How It Works</a>
    <a href="index.html">Route Guide</a>
    <a href="{prefix}#waitlist" class="nav-cta-drawer">Join the Waitlist →</a>
  </div>"""


def footer_html(prefix="../", include_osm=True):
    osm = ""
    if include_osm:
        osm = """
    <p class="footer-osm">
      Exit data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>,
      available under the Open Database License.
    </p>"""
    return f"""  <!-- FOOTER -->
  <footer>
    <div class="footer-left">
      <div class="footer-brand">
        <img src="{prefix}Kibi_Logo_Horizontal_White.png" alt="Kibi" style="height:28px;display:block;" />
      </div>
      <span class="footer-tagline">drivekibi.com</span>
      <a href="https://www.instagram.com/drivekibi" target="_blank" rel="noopener noreferrer"
         aria-label="Kibi on Instagram"
         style="color:var(--text-muted);font-size:.76rem;text-decoration:none;">
        Instagram
      </a>
      <a href="{prefix}privacy.html" class="footer-privacy">Privacy Policy</a>{osm}
    </div>
    <nav class="footer-links" aria-label="Footer navigation">
      <a href="{prefix}#how-it-works">How It Works</a>
      <a href="{prefix}#waitlist">Join Waitlist</a>
      <a href="index.html">Route Guide</a>
    </nav>
    <p class="footer-copy">&copy; 2026 Kibi. All rights reserved.</p>
  </footer>"""


NAV_JS = """
  <script>
    // Nav scroll shadow
    window.addEventListener('scroll', () => {
      document.getElementById('main-nav').style.boxShadow =
        scrollY > 20 ? '0 2px 20px rgba(0,0,0,0.3)' : '';
    }, { passive: true });

    // Hamburger / mobile drawer
    const hamburger = document.getElementById('hamburger');
    const drawer    = document.getElementById('nav-drawer');
    if (hamburger && drawer) {
      hamburger.addEventListener('click', () => {
        const isOpen = drawer.classList.toggle('open');
        hamburger.classList.toggle('open', isOpen);
        hamburger.setAttribute('aria-expanded', isOpen);
        drawer.setAttribute('aria-hidden', !isOpen);
        document.body.style.overflow = isOpen ? 'hidden' : '';
      });
      drawer.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
          drawer.classList.remove('open');
          hamburger.classList.remove('open');
          hamburger.setAttribute('aria-expanded', 'false');
          drawer.setAttribute('aria-hidden', 'true');
          document.body.style.overflow = '';
        });
      });
    }
  </script>"""


# ── Route page builder ────────────────────────────────────────────────────────

def build_route_page(data):
    slug        = data["route_slug"]
    origin      = data["origin"]
    destination = data["destination"]
    highway     = data["highway"]
    exits       = data["exits"]
    n           = data["exit_count"]

    title       = f"Best Stops: {origin} to {destination} | Kibi"
    description = (
        f"Planning a drive from {origin} to {destination} on {highway}? "
        f"Kibi scored {n} highway exits along this route. Find the best stop "
        f"for gas, food, and a bathroom — before you leave home."
    )
    canonical   = f"https://drivekibi.com/routes/{slug}.html"

    json_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": f"Best Highway Stops: {origin} to {destination}",
        "description": description,
        "author": {"@type": "Organization", "name": "Kibitzer, Inc."},
        "publisher": {"@type": "Organization", "name": "Kibitzer, Inc."},
        "mainEntityOfPage": canonical,
    }, indent=4)

    # Build table rows
    rows_html = ""
    for ex in exits:
        num   = ex.get("exit_number") or "—"
        name  = ex.get("exit_name")   or "Highway Exit"
        state = ex.get("state")       or ""
        stype = ex.get("stop_type")   or ""
        lat   = ex.get("lat", 0)
        lng   = ex.get("lng", 0)
        label = type_label(stype)

        rows_html += f"""        <tr>
          <td class="exit-num">{num}</td>
          <td class="exit-name">{name}</td>
          <td class="exit-state">{state}</td>
          <td><span class="type-badge">{label}</span></td>
          <td class="exit-coords">{lat:.4f}, {lng:.4f}</td>
        </tr>\n"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{description}" />
  <link rel="canonical" href="{canonical}" />
  <meta name="robots" content="index, follow" />

  <!-- Open Graph -->
  <meta property="og:type" content="article" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:title" content="Best Stops: {origin} to {destination} | Kibi" />
  <meta property="og:description" content="{description}" />
  <meta property="og:image" content="https://drivekibi.com/og-image.png" />

  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Lora:wght@600;700&display=swap" rel="stylesheet" />

  <!-- Favicon -->
  <link rel="icon" type="image/png" href="../Kibi_Logo_Icon_White.png" />

  <script type="application/ld+json">
{json_ld}
  </script>

  <style>
{SHARED_CSS}
  </style>
</head>
<body>

{nav_html()}

  <!-- HERO -->
  <section class="route-hero">
    <p class="breadcrumb">
      <a href="../">Kibi</a> &rsaquo; <a href="index.html">Routes</a> &rsaquo; {origin} to {destination}
    </p>
    <h1>Best Stops: {origin} to {destination}</h1>
    <p class="route-subhead">
      {n} highway exits scored along {highway} &middot;
      Kibi finds the best stop for gas, food, and a bathroom &mdash;
      so you never settle for a bad exit.
    </p>
    <div class="stat-pills">
      <span class="stat-pill">{n} Exits Scored</span>
      <span class="stat-pill">{highway}</span>
    </div>
  </section>

  <!-- EXIT TABLE -->
  <section class="exit-section">
    <p class="section-label">Highway Exits</p>
    <h2>Exits Along This Route</h2>
    <div class="exit-table-wrap">
      <table>
        <thead>
          <tr>
            <th>Exit</th>
            <th>Location</th>
            <th>State</th>
            <th>Type</th>
            <th>Coordinates</th>
          </tr>
        </thead>
        <tbody>
{rows_html}        </tbody>
      </table>
    </div>
  </section>

  <!-- CTA -->
  <section class="route-cta">
    <h2>Plan this drive with Kibi.</h2>
    <p>
      Kibi finds the single best exit for gas, food, and a bathroom &mdash;
      calculated around your vehicle&rsquo;s range. Free on iOS. No ads.
    </p>
    <span class="btn-coming-soon">Coming Soon to iOS</span>
    <span class="cta-sub">Free download &middot; iOS only</span>
  </section>

  <!-- BACK LINK -->
  <div class="back-link">
    <a href="index.html">&larr; All Routes</a>
  </div>

{footer_html()}

{NAV_JS}
</body>
</html>
"""


# ── Routes index page ─────────────────────────────────────────────────────────

def build_index_page(all_routes_data):
    cards = ""
    for data in all_routes_data:
        slug        = data["route_slug"]
        origin      = data["origin"]
        destination = data["destination"]
        highway     = data["highway"]
        n           = data["exit_count"]
        cards += f"""      <a href="{slug}.html" class="route-card">
        <span class="route-card-hw">{highway}</span>
        <h3>{origin} &rarr; {destination}</h3>
        <p class="route-card-meta">{n} exits scored</p>
        <span class="route-card-arrow">View exits &rarr;</span>
      </a>\n"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Highway Route Guides | Kibi</title>
  <meta name="description" content="Kibi scored 79,000+ US highway exits. Browse the best stops for gas, food, and a bathroom by route — before you leave home." />
  <link rel="canonical" href="https://drivekibi.com/routes/index.html" />
  <meta name="robots" content="index, follow" />

  <!-- Open Graph -->
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://drivekibi.com/routes/index.html" />
  <meta property="og:title" content="Highway Route Guides | Kibi" />
  <meta property="og:description" content="Kibi scored 79,000+ US highway exits. Browse the best stops by route." />
  <meta property="og:image" content="https://drivekibi.com/og-image.png" />

  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Lora:wght@600;700&display=swap" rel="stylesheet" />

  <!-- Favicon -->
  <link rel="icon" type="image/png" href="../Kibi_Logo_Icon_White.png" />

  <style>
{SHARED_CSS}
{INDEX_EXTRA_CSS}
  </style>
</head>
<body>

{nav_html()}

  <!-- HERO -->
  <section class="routes-hero">
    <p class="section-label" style="margin-bottom:20px;">Route Guides</p>
    <h1>Best Highway Stops by Route</h1>
    <p>
      Kibi scored 79,000+ US highway exits. Browse top stops for gas,
      food, and a bathroom by route &mdash; before you leave home.
    </p>
  </section>

  <!-- ROUTE CARDS -->
  <section class="routes-grid-section">
    <div class="routes-grid">
{cards}    </div>
  </section>

  <!-- BACK LINK -->
  <div class="back-link">
    <a href="../">&larr; Back to Kibi</a>
  </div>

{footer_html(include_osm=False)}

{NAV_JS}
</body>
</html>
"""


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    json_files = sorted(glob.glob(os.path.join(ROUTES_DIR, "*.json")))
    if not json_files:
        print("No JSON files found in routes/. Run generate_routes.py first.")
        return

    all_routes_data = []
    for path in json_files:
        with open(path) as f:
            data = json.load(f)
        all_routes_data.append(data)

        html = build_route_page(data)
        out  = os.path.join(ROUTES_DIR, f"{data['route_slug']}.html")
        with open(out, "w") as f:
            f.write(html)
        print(f"  ✓  {out}  ({data['exit_count']} exits)")

    # Hub index
    index_html = build_index_page(all_routes_data)
    index_path = os.path.join(ROUTES_DIR, "index.html")
    with open(index_path, "w") as f:
        f.write(index_html)
    print(f"  ✓  {index_path}  (hub — {len(all_routes_data)} routes)")

    print(f"\nDone. {len(all_routes_data)} route pages + 1 index page generated.")


if __name__ == "__main__":
    main()
