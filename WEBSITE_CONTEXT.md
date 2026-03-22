# KIBI WEBSITE REDESIGN — MASTER CONTEXT FILE
# Last Updated: March 2026
# Purpose: Single source of truth for the immersive scroll redesign of kibi's marketing site.
# Read this before starting any build session.

---

## 1. WHAT THIS PROJECT IS

A complete ground-up redesign of Kibi's marketing website (`index.html`), replacing the
current standard light-themed layout with an immersive, scroll-driven nighttime highway
experience. The site lives on GitHub Pages as a single `index.html` file.

**Goal**: Make someone who lands on this page feel like they're on a night drive — and leave
them wanting to download Kibi before they reach the bottom.

**Primary CTA**: App Store download (iOS)
**Secondary CTA**: Waitlist email signup (for Android / pre-launch updates)
**Audience**: Road trippers, frequent highway drivers, anyone who has ever stopped at a bad exit.

---

## 2. WHAT IS KIBI (for copy and context)

Kibi is a native iOS app — a smart road trip co-pilot. It does NOT replace Google Maps,
Apple Maps, or Waze. It wraps around them.

**One-line pitch**: "Kibi is what Google Maps would be if it actually cared about your
drive experience, your environmental impact, and your time."

**Core problem**: On long highway drives, drivers waste miles stopping at bad exits,
miss meal windows, or stop 3 separate times for gas, food, and bathrooms when one good
exit would have covered all three.

**What Kibi does**:
1. User enters a destination (e.g. Chicago → Atlanta)
2. Kibi calculates pitstop intervals based on vehicle tank range (with 15% safety buffer)
3. Kibi finds the BEST single exit — gas + food + bathroom grouped, scored by rating/safety
4. User confirms stops
5. Kibi deep-links into Google Maps / Apple Maps / Waze with waypoints pre-loaded
6. Kibi tracks CO₂ and trip stats in the background
7. Trip summary on arrival

**What Kibi is NOT**: A navigation app, review platform, or subscription service. No ads in v1.

**Status**: Early Access iOS app. App Store URL: https://apps.apple.com/app/kibi/id6760270037

---

## 3. BRAND TOKENS

```css
/* Core palette */
--kibi-black:       #0B0E0C;   /* near-black background, slightly warm */
--kibi-green:       #2EBD7A;   /* primary brand green */
--kibi-green-glow:  rgba(46,189,122,0.35);  /* for neon glow effects */
--kibi-green-dim:   rgba(46,189,122,0.12);  /* subtle green tint */
--kibi-white:       #F0F4F1;   /* off-white for body text */
--kibi-muted:       rgba(240,244,241,0.45); /* secondary/body copy */
--kibi-road:        #141A16;   /* slightly lighter than bg — road surface */
--kibi-amber:       #F5A623;   /* headlight/billboard warm accent */
--kibi-amber-glow:  rgba(245,166,35,0.25);

/* Typography */
--font-display: "Fraunces", serif;        /* headlines — already used in current site */
--font-body:    "DM Sans", sans-serif;    /* body — already used in current site */

/* Neon glow recipe (CSS text-shadow) */
--neon-green: 0 0 8px #2EBD7A, 0 0 20px rgba(46,189,122,0.6), 0 0 40px rgba(46,189,122,0.3);
--neon-white: 0 0 8px #ffffff, 0 0 20px rgba(255,255,255,0.5), 0 0 35px rgba(255,255,255,0.2);
--neon-amber: 0 0 8px #F5A623, 0 0 20px rgba(245,166,35,0.5), 0 0 40px rgba(245,166,35,0.3);
```

**Logo files available** (in project):
- `Kibi_Logo_Wordmark_White.png` — use in nav and hero
- `Kibi_Logo_Icon_White.png` — use as standalone icon in CTA
- `Kibi_Logo_Primary_White.png` — full lockup with hummingbird

---

## 4. TECH STACK

| Layer               | Technology                     | Notes                                    |
|---------------------|-------------------------------|------------------------------------------|
| Scroll engine       | GSAP + ScrollTrigger           | CDN: gsap.com/docs/v3/Installation       |
| Fonts               | Google Fonts CDN               | Fraunces + DM Sans (already in site)     |
| Graphics            | CSS + SVG (inline)             | No WebGL, no 3D, no external images      |
| Hosting             | GitHub Pages                   | Single `index.html`                      |
| Email capture       | Formspree                      | `https://formspree.io/f/[FORM_ID]`       |
| App screenshots     | PNG exports from React proto   | `KIBI_v1_Demo_Template.jsx` source       |

**GSAP CDN links** (add to `<head>`):
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
```

**No license issue**: GSAP ScrollTrigger is free for "no-charge" end products.
For a commercial app (post-monetization), upgrade to Business Green ($150 one-time).

---

## 5. SCROLL ARCHITECTURE OVERVIEW

The site is structured as a series of **scroll scenes**. On desktop, GSAP ScrollTrigger
pins each scene and runs its animations as the user scrolls through a defined scroll range.
On mobile (`max-width: 768px`), all GSAP animations are disabled and a flat,
single-column layout is shown instead.

**Total scroll height (desktop)**: ~600vh (6 screens worth of scroll)
**Each scene**: pinned to viewport, scroll progress drives animation timeline

### Scene Map

| # | Scene Name           | Scroll Range | Primary Animation                          | Key Message                          |
|---|----------------------|-------------|---------------------------------------------|--------------------------------------|
| 0 | Hero / Pre-scroll    | 0vh         | CSS fade-in on load (no scroll needed)     | CTA above fold, download badge       |
| 1 | Enter the Road       | 0–15%       | Parallax sky/trees/road layers             | Atmosphere — you start driving       |
| 2 | Dashboard Appears    | 15–35%      | Dashboard slides up, app UI fades in       | Kibi personalizes to your car        |
| 3 | On the Road          | 35–50%      | Road lines speed up, CO₂ counter ticks     | Background tracking, feels alive     |
| 4 | Exit Sign            | 50–62%      | Sign swings down from top of viewport      | Core feature: the scored exit        |
| 5 | Billboard 1          | 62–70%      | Billboard slides in from right             | "No more guessing at exits."         |
| 6 | Billboard 2          | 70–78%      | Billboard slides in from left              | "Works with Maps, Waze, Google Maps" |
| 7 | Billboard 3          | 78–85%      | Green neon billboard — slower reveal       | "Track your CO₂. Every mile."        |
| 8 | Exit Ramp / Arrive   | 85–92%      | Road decelerates, car slows, "arrived"     | "You planned that perfectly."        |
| 9 | CTA / Close          | 92–100%     | Clean dark — logo glow, App Store badge    | Download Kibi.                       |

### Preserved Content Sections (after scroll experience, standard layout)
These scroll naturally BELOW the immersive section:
- How It Works (4 steps)
- Road Trip Calculator + Boarding Pass ← keep exactly, restyle to dark theme
- Features / Pillars (condensed to 3 cards)
- Eco Tracking (2-column, dark)
- Waitlist / Email capture
- Footer

### Removed from current site (not consumer-facing):
- "The Opportunity" / Market section (investor pitch content — cut entirely)
- Exit Coverage heatmap link (keep in footer only, low prominence)

---

## 6. SCENE VISUAL SPECS

### SVG Road Scene (used across scenes 1–8)
Built from stacked absolutely-positioned layers. All CSS/SVG — no images needed.

```
Layer order (back to front):
1. Sky — deep near-black gradient (#0B0E0C → #0D1510), subtle star dots
2. Horizon glow — faint amber/green gradient strip at horizon line
3. Treeline silhouette — low black SVG jagged shape
4. Road surface — dark rectangle, perspective trapezoid
5. Lane dashes — white dashes, animated translateY to simulate motion
6. Road edge lines — thin white solid lines left/right
```

**Parallax speeds** (scroll multiplier):
- Sky: 0.1x (barely moves)
- Trees: 0.3x
- Road: 1.0x (tied to scroll directly)
- Lane dashes: CSS `@keyframes` loop, speed increases in Scene 3

### Dashboard Scene (Scene 2)
Flat illustrated dashboard panel slides up from bottom:
- Dark panel with green instrument cluster glow
- Phone mount in center: shows app UI screenshot (from React prototype or static mockup)
- Preference toggles animate: Year → Make → Model dropdowns check off
- Fuel gauge needle sweeps

**Asset needed**: Screenshot of vehicle setup screen from React prototype.
Fallback: Use the existing phone mockup CSS from current `index.html` (it's already built).

### Exit Sign (Scene 4)
Realistic US green highway exit sign, built in CSS/SVG:
```
┌────────────────────────────────────────┐
│  EXIT                              →   │
│   94                                   │
│                              1/2 MILE  │
│  ⛽ Shell · 🍔 Wendy's · 🚻 Clean    │
│  ★★★★  Kibi Score: 91                │
└────────────────────────────────────────┘
```
- White text on MUTCD green (#234F1E with #2EBD7A tint for Kibi brand)
- White border
- Swings in with `rotate3D` CSS transform on scroll trigger
- Gantry arms top (two thin black vertical lines + horizontal bar)

### Billboards (Scenes 5–7)
Standard rectangular billboard on a pole:
- Dark frame/structure
- Text glows (CSS text-shadow neon recipe above)
- Billboard 1 & 2: white neon text
- Billboard 3: all Kibi green neon text

Billboard positions:
- Scene 5: right side of road, slides in from off-screen right
- Scene 6: left side of road, slides in from off-screen left
- Scene 7: centered/ahead on road, zooms slightly toward viewer

---

## 7. COPY — LOCKED

### Hero
```
Badge:         Early Access · iOS
H1:            Your road trip,
               planned perfectly.
Subhead:       Kibi finds the best exit every time — gas, food,
               and a clean bathroom at one stop. No detours. No regrets.
CTA Button:    Download on the App Store  [badge]
Scroll hint:   scroll to drive ↓
```

### Stats Bar (below hero, animated in)
```
79,000+   Highway exits mapped
49,000+   Vehicles supported
230M+     US licensed drivers
```

### Scene 2 — Dashboard
```
Headline:      "Kibi learns your car."
Sub:           "49,000+ vehicles. Every tank size. Every fuel type."
```

### Scene 3 — On the Road
```
Float text:    "Kibi runs quietly in the background.
                Tracking every mile."
Counter label: "CO₂ tracked this trip"
Miles label:   "miles driven"
```

### Scene 4 — Exit Sign
```
Exit number:   94
Distance:      1/2 mile
Businesses:    ⛽ Shell · 🍔 Wendy's · 🚻 Clean Restrooms
Score:         Kibi Score: 91 / 100
```
```
Beside sign:   "One stop.
                Gas. Food. Bathroom.
                Already scored for you."
```

### Scene 5 — Billboard 1
```
Main:          "No more guessing
                at exits."
Sub:           "Kibi scores every exit so you always
                stop somewhere worth it."
```

### Scene 6 — Billboard 2
```
Main:          "Works with
                Google Maps.
                Apple Maps. Waze."
Sub:           "Kibi plans it. Your nav app drives it."
Logo hints:    [small muted logos fade in]
```

### Scene 7 — Billboard 3 (Eco, all green neon)
```
Main:          "Track your CO₂.
                Every mile."
Counter:       [animated: 4.7 kg tracked]
Sub:           "Because your drive has an impact.
                Kibi shows you exactly what it is."
```

### Scene 8 — Exit Ramp
```
Main:          "You planned that perfectly."
Stats:         "312 miles  ·  3 stops  ·  All worth it."
```

### Scene 9 — Final CTA
```
Headline:      "Download Kibi.
                Drive smarter."
Badge:         [App Store badge — large]
Sub:           "Free. No ads. No subscription."
```

### How It Works (post-scroll section)
```
Tag:     How It Works
Title:   Four steps to a smarter drive
Sub:     Kibi wraps around your existing navigation — no turn-by-turn,
         no replacing what works. Just better stops, every time.

Step 1:  Set Your Vehicle
         Pick from 49,000+ EPA-verified vehicles. Kibi fills in your
         MPG, fuel type, and range automatically.

Step 2:  Enter Your Destination
         Type where you're headed. Kibi calculates where you need to
         stop based on your range and preferences.

Step 3:  Get the Best Exit
         Kibi scores every exit on your route and surfaces the single
         best stop — gas, food, and a bathroom at one place.

Step 4:  Navigate & Track
         Kibi launches Google Maps, Apple Maps, or Waze with stops
         pre-loaded. Tracks your CO₂ the whole way.
```

### Road Trip Calculator
```
Tag:     Try It
Title:   Plan your drive.
         See your impact.
Sub:     Enter any two cities and get a full breakdown — drive time,
         pitstops, fuel cost, and your real CO₂ footprint.
```

### Waitlist
```
Icon:    🚗 (or hummingbird)
Title:   "Be first on the road."
Sub:     "Kibi is live on iOS. Android and new features are coming.
          Drop your email and we'll let you know when it's your turn."
CTA:     Get Early Access
Proof:   Free to download  ·  No spam  ·  Unsubscribe anytime
```

### Marquee (scrolling ticker strip — Kibi green background)
```
Smart Pitstop Planning  ◆  EPA-Verified Vehicle Data  ◆
Real-Time CO₂ Tracking  ◆  79,000+ Highway Exits  ◆
Google Maps · Apple Maps · Waze  ◆  49,000+ Vehicles  ◆
Zero Ads  ◆  Free on the App Store
```

---

## 8. NAVIGATION

**Desktop nav** (fixed, dark, semi-transparent):
```
[Kibi logo — white wordmark]          [How It Works] [Features] [Calculator] [Download App ↗]
```

**Mobile nav**: Hamburger → full-screen drawer (dark theme, same links)

Nav background: `rgba(11,14,12,0.85)` with `backdrop-filter: blur(16px)`
Nav scrolled: add subtle bottom border `rgba(46,189,122,0.2)`

---

## 9. MOBILE LAYOUT (≤768px)

GSAP scroll experience is **fully disabled** on mobile.
Instead: standard single-column stacked layout with dark theme.

```
Mobile sections in order:
1. Hero — full screen, centered, download badge
2. Stats bar — 3 stats in a row
3. Marquee strip
4. How It Works — 4 cards, single column
5. Road Trip Calculator — full width
6. Features — 3 cards, stacked
7. Eco section — single column
8. Waitlist
9. Footer
```

App screenshot / phone mockup: Use the existing CSS phone mockup from current `index.html`
(already works well, just reskin to dark theme).

---

## 10. ROAD TRIP CALCULATOR — PRESERVE EXACTLY

The road trip calculator + boarding pass widget is a strong differentiator.
**Do not simplify or remove it.** Port the existing JS logic exactly — it works.

Changes for the redesign:
- Restyle form to dark theme (dark input fields, green accents)
- Boarding pass: already dark-themed in current site — minimal changes needed
- Keep all CO₂ comparison cards (trees, burgers, home percentage, flight comparison)
- Keep the barcode generator
- Keep Formspree integration

---

## 11. FORMSPREE SETUP (MANUAL STEP — do before final deploy)

The waitlist form uses Formspree for zero-backend email capture.
1. Go to https://formspree.io — create free account
2. Create a new form → copy the form ID (looks like `xpwzabcd`)
3. Replace `[FORMSPREE_FORM_ID]` placeholder in the HTML with your actual ID
4. Test by submitting the form — check your Formspree dashboard

---

## 12. APP STORE LINK

Current App Store URL:
`https://apps.apple.com/app/kibi/id6760270037`

Use this as the `href` for all App Store download buttons.
Use the official Apple App Store badge SVG (available free from Apple's marketing resources).

---

## 13. FILES REFERENCED

| File                              | Used In             | Notes                                  |
|-----------------------------------|---------------------|----------------------------------------|
| `index.html`                      | Main site           | The deliverable                        |
| `Kibi_Logo_Wordmark_White.png`    | Nav, footer         | Must be in same repo directory         |
| `Kibi_Logo_Icon_White.png`        | CTA section         | Hummingbird icon only                  |
| `Kibi_Logo_Primary_White.png`     | Loading screen opt. | Full lockup                            |
| `kibi-demo.html`                  | Optional demo embed | Can keep as separate file or cut       |
| `kibi_exit_heatmap.html`          | Footer link only    | No longer in main nav                  |

---

## 14. PERFORMANCE REQUIREMENTS

- Fonts: Google Fonts CDN with `display=swap` (already done in current site)
- GSAP: load from cdnjs CDN (no npm needed)
- Images: WebP where possible, PNG fallback; all under 200KB each
- No external image URLs — everything self-hosted in GitHub repo
- Target: Lighthouse Performance > 85 on desktop
- No cookie banners, trackers, or analytics in v1 (keeps it clean and fast)

---

## 15. WHAT NOT TO BUILD (scope guard)

- ❌ No 3D / WebGL / Three.js
- ❌ No video backgrounds (performance killer on mobile)
- ❌ No "The Opportunity" / market slide (investor content, not for consumers)
- ❌ No social media links (none exist yet)
- ❌ No blog or content section
- ❌ No contact form (use waitlist email instead)
- ❌ No cookie banner
- ❌ No React / build step — must be pure HTML/CSS/JS, single file

---

## 16. DEFINITION OF DONE

The site is complete when:
- [ ] All 9 scroll scenes animate correctly on Chrome desktop
- [ ] Safari desktop: scroll animations work
- [ ] Mobile (≤768px): flat layout renders correctly, no broken scroll
- [ ] iOS Safari (test on actual phone): layout is correct, CTA is tappable
- [ ] App Store link works
- [ ] Waitlist form submits successfully via Formspree
- [ ] Road trip calculator runs correctly (geocoding + boarding pass)
- [ ] All logo images load (not broken)
- [ ] Lighthouse Performance > 80
- [ ] No console errors
- [ ] Pushed to GitHub Pages and live at public URL
