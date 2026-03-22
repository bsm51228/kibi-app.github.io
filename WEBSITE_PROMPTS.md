# KIBI WEBSITE REDESIGN — STEP-BY-STEP BUILD PROMPTS
# Last Updated: March 2026
#
# HOW TO USE THIS FILE:
# - Work through steps in order. Do not skip ahead.
# - Steps marked [MANUAL] require you to do something before prompting.
# - Steps marked [PROMPT → CLAUDE CODE] are copy-paste prompts.
# - Steps marked [PROMPT → CLAUDE.AI] are for this chat (planning/review).
# - Replace anything in [BRACKETS] with your actual values before pasting.
#
# Paste WEBSITE_CONTEXT.md at the start of every new Claude Code session.

---

## ═══════════════════════════════════════════
## PHASE 0 — SETUP (manual steps, no prompting)
## ═══════════════════════════════════════════

### STEP 0.1 [MANUAL] — Repo & file prep (COMPLETED)
```
1. Open your kibi GitHub repo (the one currently hosting index.html)
2. Rename your current index.html → index_OLD.html (backup)
3. Confirm these logo files are in the root of the repo:
   - Kibi_Logo_Wordmark_White.png
   - Kibi_Logo_Icon_White.png
   - Kibi_Logo_Primary_White.png
4. Confirm kibi-demo.html is in the same repo root
5. Note your GitHub Pages URL (e.g. https://[username].github.io/[repo]/)
```

### STEP 0.2 [MANUAL] — Formspree account (COMPLETED)
```
1. Go to https://formspree.io
2. Sign up with your email
3. Click "New Form" → name it "Kibi Waitlist"
4. Copy your form endpoint ID: xzdjlezp
5. Save it — you'll paste it into a prompt later
```

### STEP 0.3 [MANUAL] — Get App Store badge (COMPLETED)
```
1. Go to https://developer.apple.com/app-store/marketing/guidelines/
2. Download "Download on the App Store" badge (black version, SVG or PNG)
3. Save as: appstore-badge.svg (or .png) in your repo root
```

### STEP 0.4 [MANUAL] — Take app screenshots (COMPLETED)
```
Take 1-2 screenshots from your React prototype or Xcode simulator showing:
  (a) The vehicle setup screen (Year/Make/Model dropdowns)
  (b) The active trip / pitstop screen

Export as PNG, name them:
  - screenshot-setup.png
  - screenshot-trip.png

Add to repo root. These will be used in the Dashboard scene (Scene 2).
If you don't have these yet, the prompts will use the existing CSS phone
mockup as a fallback — note this in Step 2.
```

---

## ═══════════════════════════════════════════
## PHASE 1 — SCAFFOLD THE DARK SITE SHELL
## ═══════════════════════════════════════════
# Goal: Create a new index.html with the correct dark theme tokens,
# fonts, nav, and empty section placeholders. No scroll animations yet.

### STEP 1.1 [PROMPT → CLAUDE CODE]
```
Read WEBSITE_CONTEXT.md first, then:

Create a new index.html file with the following:

1. DOCTYPE, meta tags, title "Kibi — Your Road Trip Co-Pilot"
2. Google Fonts CDN links for Fraunces (weights 300,700,900,italic) and DM Sans (300,400,500,600)
3. GSAP + ScrollTrigger CDN links from cdnjs.cloudflare.com (v3.12.5)
4. CSS variables block with ALL tokens from WEBSITE_CONTEXT.md Section 3
5. CSS reset (box-sizing, margin, padding, scroll-behavior: smooth)
6. Body: background #0B0E0C, color #F0F4F1, font-family DM Sans
7. A fixed dark nav bar with:
   - Left: <img src="Kibi_Logo_Wordmark_White.png" height="28" alt="Kibi">
   - Right links: "How It Works" | "Features" | "Calculator" | Download button (green pill, links to https://apps.apple.com/app/kibi/id6760270037)
   - Mobile hamburger (hidden on desktop, shown on mobile ≤768px)
   - Nav background: rgba(11,14,12,0.85) with backdrop-filter blur(16px)
8. Empty section placeholders with IDs: #scroll-experience, #how, #calculator, #features, #eco, #waitlist
9. Footer with: logo left, "© 2025 Kibi · Privacy Policy" right (muted)

Do not add any content inside the sections yet — just the scaffolding.
Do not add any GSAP animation code yet.
Make it a single self-contained HTML file.
```

### STEP 1.2 [MANUAL — verify before continuing]
```
1. Open index.html in browser
2. Check: dark background loads, nav appears correctly
3. Check: logo image loads (white wordmark visible)
4. Check: nav links scroll to empty sections
5. Check: mobile hamburger appears at ≤768px
If anything is broken, fix before moving to Phase 2.
```

---

## ═══════════════════════════════════════════
## PHASE 2 — BUILD THE ROAD SCENE LAYERS
## ═══════════════════════════════════════════
# Goal: Build the base highway scene that all scroll animations sit on top of.
# This is a fixed background with layered SVG/CSS elements.

### STEP 2.1 [PROMPT → CLAUDE CODE]
```
In the existing index.html, replace the empty #scroll-experience section with
a full-height (100vh) fixed scene container. Inside it, build the following
CSS/SVG highway scene using stacked absolutely-positioned layers:

Layer 1 — Sky (bottom of stack, z-index 1):
  Full screen. Background: radial gradient from #0D1510 at center to #0B0E0C.
  Add 30-40 tiny star dots (2-3px, white, 10-30% opacity) scattered randomly
  across the top 60% of the sky using absolute positioning or SVG circles.
  No images — pure CSS/SVG only.

Layer 2 — Horizon glow (z-index 2):
  A thin (80px tall) horizontal strip at ~65% from top.
  Gradient: transparent → rgba(46,189,122,0.08) → rgba(245,166,35,0.06) → transparent
  Blurred slightly with filter: blur(12px)

Layer 3 — Treeline silhouette (z-index 3):
  SVG shape at bottom 35% of scene. Jagged/organic dark silhouette of trees.
  Fill: #080C09 (darker than background for depth).
  Width: 100%, position absolute bottom.
  Create roughly 15-20 irregular triangular tree shapes of varying heights.

Layer 4 — Road surface (z-index 4):
  CSS trapezoid shape (wider at bottom, narrow point at horizon line).
  Color: #141A16
  Position: centered, bottom of viewport.
  Use clip-path: polygon() to create perspective.
  Example: polygon(30% 100%, 70% 100%, 56% 0%, 44% 0%)
  (adjust % values to look like a real road going to a vanishing point)

Layer 5 — Road edge lines (z-index 5):
  Two thin white lines (2px wide) following the road trapezoid edges.
  Opacity: 0.3
  Also CSS clip-path or SVG lines.

Layer 6 — Lane dashes (z-index 6):
  A series of white dashes (8px wide, 40px tall, 40px gap) running down
  the center of the road.
  Animate them with a CSS @keyframes animation: translateY from -80px to 0
  repeating infinitely over 0.8s, creating the illusion of forward motion.
  Name this animation: --dash-speed variable that we can change later.

Layer 7 — Dashboard overlay (z-index 7, initially opacity 0):
  A div with id="dashboard-panel". Dark rounded rect at bottom of viewport.
  Width: 80%, centered. Height: ~40vh. Background: #111A14.
  Leave empty for now — we'll populate it in Phase 3.

Give the overall container id="road-scene" and position: fixed with
width: 100% height: 100vh top:0 left:0.
The section#scroll-experience should be height: 600vh (the scroll canvas).
```

### STEP 2.2 [MANUAL — verify]
```
1. Open in browser. You should see a dark highway scene without scrolling.
2. Check: stars visible in sky
3. Check: lane dashes are animating (white dashes moving downward)
4. Check: road has perspective (narrows toward horizon)
5. Check: treeline silhouette is visible
If it looks like a night highway, proceed. If not, refine before continuing.
```

---

## ═══════════════════════════════════════════
## PHASE 3 — HERO SCENE (Scene 0)
## ═══════════════════════════════════════════
# Goal: Build the above-the-fold content that loads before any scrolling.
# CTA must be visible without scrolling on any screen size.

### STEP 3.1 [PROMPT → CLAUDE CODE]
```
Inside the road scene overlay (above the road, z-index 20), add the hero
content. This should appear immediately on page load with CSS animation
(not GSAP — no scroll dependency for the hero):

1. Badge pill (top, centered or left-aligned):
   Text: "Early Access · iOS"
   Style: small rounded pill, border: 1px solid rgba(46,189,122,0.4),
   color: #2EBD7A, background: rgba(46,189,122,0.1), font-size 0.72rem
   Pulse dot on left (same as current site's hero-badge-dot)
   Animate in: fadeUp 0.5s 0.1s forwards

2. H1 headline (Fraunces, 900, 4rem desktop / 2.4rem mobile):
   "Your road trip,
    planned perfectly."
   Color: white. Letter-spacing: -0.03em. Line-height: 1.0.
   Animate in: fadeUp 0.6s 0.25s forwards

3. Subhead (DM Sans, 300, 1rem):
   "Kibi finds the best exit every time — gas, food, and a clean bathroom
    at one stop. No detours. No regrets."
   Color: rgba(240,244,241,0.65). Max-width: 480px.
   Animate in: fadeUp 0.6s 0.4s forwards

4. App Store download button:
   - Use <a> tag linking to: https://apps.apple.com/app/kibi/id6760270037
   - Contains <img src="appstore-badge.svg" alt="Download on the App Store" height="48">
   - Add subtle green glow on hover: box-shadow with kibi-green-glow
   Animate in: fadeUp 0.6s 0.55s forwards

5. Scroll hint:
   Text: "scroll to drive ↓"
   Style: tiny, muted (opacity 0.35), centered at bottom of hero area.
   Animate: gentle up-down bob (CSS keyframe), loops.
   Should fade out once user scrolls past 5% (handle with a simple scroll
   event listener in JS: if scrollY > 50, set opacity to 0 with transition).

Position all hero text in the upper-center or upper-left of the viewport,
above the road surface (road occupies roughly bottom 45% of viewport).
```

### STEP 3.2 [MANUAL — verify]
```
1. Open in browser. The headline, subhead, and App Store badge should
   appear on load without any scrolling.
2. Check that the App Store link opens correctly.
3. Check the scroll hint arrow bobs gently and disappears on scroll.
4. Mobile check: text is readable, badge is tappable (min 44px height).
```

---

## ═══════════════════════════════════════════
## PHASE 4 — GSAP SCROLL SCENES (Scenes 1–4)
## ═══════════════════════════════════════════
# Goal: Wire up GSAP ScrollTrigger for the first half of the scroll journey.

### STEP 4.1 [PROMPT → CLAUDE CODE]
```
Now add GSAP ScrollTrigger animations. The scroll container is
section#scroll-experience (height: 600vh). The road scene is
position: fixed (already done).

Register ScrollTrigger: gsap.registerPlugin(ScrollTrigger)

Create a master ScrollTrigger that scrubs through all scenes:
  trigger: "#scroll-experience"
  start: "top top"
  end: "bottom bottom"
  scrub: 1.5

Scene 1 — Enter the Road (0–15% of scroll):
  - Sky layer: translateY from 0 to -20px (very slow drift)
  - Treeline: translateY from 0 to -60px (slightly faster)
  - Slow lane dash animation speed at start, build to faster
  - Fade out the hero text slightly (opacity 1 → 0.3) so user knows
    to look at the road

Scene 2 — Dashboard Appears (15–35%):
  - #dashboard-panel: translateY from 100% to 0 (slides up from bottom)
  - #dashboard-panel opacity: 0 → 1
  - Hero text: fully fade out (opacity → 0)
  - Inside dashboard, these elements stagger in one by one as scroll
    progresses through this range:
    (a) Text: "Kibi learns your car." — fadeIn
    (b) Vehicle row: "2023 Honda Accord · 32 MPG" — fadeIn + slight translateX
    (c) Preference icons: ⛽ 🍔 🚻 ☕ — stagger in
    (d) Subtext: "49,000+ vehicles. Every tank size. Every fuel type." — fadeIn

Scene 3 — On the Road (35–50%):
  - Lane dashes: increase animation duration from 0.8s to 0.3s
    (use a JS variable to update the CSS animation-duration dynamically)
  - A floating text overlay fades in, centered:
    Line 1: "Kibi runs quietly in the background."
    Line 2: "Tracking every mile."
    Style: DM Sans, 1.1rem, muted white, centered
  - A small stat counter appears bottom-right:
    "18.4 kg CO₂" with label "tracked this trip"
    Count up animation: 0 → 18.4 over this scroll range
  - Dashboard panel fades back out (opacity → 0)

Scene 4 — Exit Sign (50–62%):
  - An exit sign element (#exit-sign) with id already in HTML:
    - Starts: translateY(-200px) rotate3d(1,0,0,-45deg) opacity 0
    - Animates to: translateY(0) rotate3d(1,0,0,0deg) opacity 1
    - Then holds, then on exit from this scene: slides back up
  - Text beside the sign fades in:
    "One stop. Gas. Food. Bathroom. Already scored for you."

Build the exit sign HTML/CSS inline. Use the spec from WEBSITE_CONTEXT.md
Section 6 (green sign, white border, Kibi Score). Add it to the road scene
as an absolutely positioned element, initially off-screen top, z-index 25.

Add all this GSAP code in a <script> block at bottom of body, inside
window.addEventListener('load', ...) to ensure DOM is ready.
```

### STEP 4.2 [MANUAL — verify scenes 1–4]
```
1. Scroll slowly from top. Check:
   - Sky/trees parallax feels natural
   - Dashboard slides up smoothly around 15% scroll
   - Vehicle info and preferences stagger in
   - Road speed increases around 35%
   - Exit sign swings in around 50%
2. Common issues to watch for:
   - GSAP not finding elements (check IDs match)
   - Dashboard sliding in too fast/slow (adjust scrub value)
   - Exit sign rotation looks unnatural (adjust rotate3d values)
3. If animations feel wrong, adjust the ScrollTrigger start/end percentages
   until each scene feels right — this is judgment-based, iterate until
   it feels smooth.
```

---

## ═══════════════════════════════════════════
## PHASE 5 — BILLBOARD SCENES (Scenes 5–7)
## ═══════════════════════════════════════════

### STEP 5.1 [PROMPT → CLAUDE CODE]
```
Add three billboard elements to the road scene and wire their GSAP animations.

Build billboard HTML structure (reusable, styled with CSS):
Each billboard has:
  - A vertical pole (thin rect, dark gray)
  - A rectangular sign board (dark bg, slight border)
  - Text inside with neon glow effect

CSS neon glow for billboard text:
  white: text-shadow: 0 0 8px #fff, 0 0 20px rgba(255,255,255,0.5)
  green: text-shadow: 0 0 8px #2EBD7A, 0 0 20px rgba(46,189,122,0.6), 0 0 40px rgba(46,189,122,0.3)

Add these three billboard divs inside #road-scene, all initially off-screen:

Billboard 1 (#billboard-1):
  Position: right side of road, initially translateX(120%)
  Content:
    Large text (Fraunces, bold): "No more guessing at exits."
    Small text (DM Sans): "Kibi scores every exit so you always stop somewhere worth it."
  Neon color: white

Billboard 2 (#billboard-2):
  Position: left side of road, initially translateX(-120%)
  Content:
    Large text: "Works with Google Maps. Apple Maps. Waze."
    Small text: "Kibi plans it. Your nav app drives it."
  Neon color: white
  Also add three small muted logo labels: [G] Maps · Apple Maps · Waze (text, no images)

Billboard 3 (#billboard-3):
  Position: center/ahead, initially scale(0.6) opacity(0)
  Content:
    Large text: "Track your CO₂. Every mile."
    A counter: "4.7 kg" with label "tracked this trip"
    Small text: "Because your drive has an impact. Kibi shows you exactly what it is."
  Neon color: ALL green (#2EBD7A) — text, border, counter

GSAP animations:

Scene 5 (62–70% scroll):
  Billboard 1: translateX(120%) → translateX(0), opacity 0 → 1
  Hold for 30% of scene, then translate back off-screen

Scene 6 (70–78% scroll):
  Billboard 2: translateX(-120%) → translateX(0), opacity 0 → 1
  Hold, then translate back off-screen

Scene 7 (78–85% scroll):
  Billboard 3: scale(0.6) opacity(0) → scale(1) opacity(1)
  CO₂ counter: count up from 0 to 4.7 as scroll progresses
  Hold, then fade out

All three billboards should feel like you're driving past them on a real highway —
they come into frame, you pass by, they disappear behind you.
```

---

## ═══════════════════════════════════════════
## PHASE 6 — EXIT RAMP + FINAL CTA (Scenes 8–9)
## ═══════════════════════════════════════════

### STEP 6.1 [PROMPT → CLAUDE CODE]
```
Add the final two scenes to the GSAP scroll timeline:

Scene 8 — Exit Ramp (85–92% scroll):
  - Slow lane dashes back to original slow speed (reverse of Scene 3 speedup)
  - Road surface: animate a slight curve/rotation to suggest turning off highway
    (subtle: slight rotateZ of the road trapezoid, 0 → 3deg)
  - Fade in centered text overlay:
    Line 1 (Fraunces, large): "You planned that perfectly."
    Line 2 (DM Sans, small, muted): "312 miles · 3 stops · All worth it."
  - Small Kibi Score badge appears: "Trip Score: 9.1 / 10"

Scene 9 — Final CTA (92–100% scroll):
  - Entire road scene fades out (opacity 1 → 0)
  - A clean dark div (#final-cta) fades in (opacity 0 → 1) over it
  - Contents of #final-cta:
    - <img src="Kibi_Logo_Icon_White.png" width="64" alt="Kibi"> with subtle pulse glow
    - H2 (Fraunces, 900, 3rem): "Download Kibi. Drive smarter."
    - p: "Free. No ads. No subscription."
    - App Store badge (same as hero)
    - Optional: email input for waitlist as secondary option

Position #final-cta: position fixed, full screen, background #0B0E0C,
z-index 50, centered flex layout.
```

### STEP 6.2 [MANUAL — verify full scroll journey]
```
Full scroll test checklist:
  [ ] Hero text visible immediately on load
  [ ] Scene 1: slight parallax movement as you start scrolling
  [ ] Scene 2: dashboard slides up, vehicle info appears
  [ ] Scene 3: speed increases, CO₂ counter ticks up
  [ ] Scene 4: exit sign swings in convincingly
  [ ] Scene 5: right-side billboard slides in, holds, leaves
  [ ] Scene 6: left-side billboard slides in, holds, leaves
  [ ] Scene 7: centered green billboard zoom-in
  [ ] Scene 8: road slows, "You planned that perfectly." appears
  [ ] Scene 9: clean dark CTA with App Store badge
  [ ] No jank, no jumps, scrub feels smooth
  [ ] Entire journey feels like it takes ~30–45 seconds at normal scroll pace
```

---

## ═══════════════════════════════════════════
## PHASE 7 — POST-SCROLL SECTIONS (standard layout, dark theme)
## ═══════════════════════════════════════════
# These sections sit BELOW the 600vh scroll experience and scroll normally.

### STEP 7.1 [PROMPT → CLAUDE CODE]
```
After the #scroll-experience section, add the following standard content
sections. All should use the dark Kibi theme (--kibi-black background,
white/muted text, green accents). Style them cleanly — no scroll animations
needed here, just solid CSS layout.

Section: Stats Bar
  A full-width dark strip (background: rgba(46,189,122,0.06), border top/bottom)
  Three stats side by side, centered:
  - "79,000+" / "Highway exits mapped"
  - "49,000+" / "Vehicles supported"
  - "230M+" / "US licensed drivers"
  Stat numbers: Fraunces, 900, 2.5rem, color #2EBD7A
  Labels: DM Sans, 300, 0.75rem, muted

Section: Marquee Strip
  Identical logic to current site marquee, but:
  Background: #2EBD7A (Kibi green)
  Text: #0B0E0C (black)
  Items: Smart Pitstop Planning ◆ EPA-Verified Vehicle Data ◆ Real-Time CO₂ Tracking ◆
         79,000+ Highway Exits ◆ Google Maps · Apple Maps · Waze ◆ 49,000+ Vehicles ◆
         Zero Ads ◆ Free on the App Store
  (duplicate the items for seamless loop)

Section: How It Works (#how)
  Tag: "How It Works"
  Title (Fraunces): "Four steps to a smarter drive"
  Sub: "Kibi wraps around your existing navigation — no turn-by-turn, no replacing
        what works. Just better stops, every time."
  4 step cards in a 2x2 grid (desktop) / 1 column (mobile):
    01 🚗 Set Your Vehicle — text from WEBSITE_CONTEXT.md Section 7
    02 📍 Enter Your Destination — text from WEBSITE_CONTEXT.md Section 7
    03 ⭐ Get the Best Exit — text from WEBSITE_CONTEXT.md Section 7
    04 🗺️ Navigate & Track — text from WEBSITE_CONTEXT.md Section 7
  Card style: dark border, slight green hover state, step number large and muted

Section: Features (#features)
  Tag: "Features"
  Title: "Everything your drive needs."
  3 feature cards in a row (desktop) / stacked (mobile):
    Card 1: 🎯 Smart Exit Scoring
      "Kibi scores every exit on your route — gas, food, bathrooms — and surfaces
       the single best stop. Every time."
    Card 2: 🌿 Real-Time CO₂ Tracking
      "Kibi calculates your exact emissions using EPA-verified data for your specific
       vehicle. Not an average. Your actual car."
    Card 3: 🗺️ Works With Your Nav App
      "Kibi deep-links into Google Maps, Apple Maps, or Waze with all stops
       pre-loaded. No switching apps mid-drive."
  Card style: border: 1px solid rgba(46,189,122,0.2), hover: glow border

Use simple IntersectionObserver fade-in reveals (class="reveal") for all cards.
```

### STEP 7.2 [PROMPT → CLAUDE CODE]
```
Now port the Road Trip Calculator from the current index.html (which I'll
paste below) into the new dark-themed site.

[PASTE THE CALCULATOR HTML/CSS/JS FROM YOUR OLD index.html HERE]
— This is lines ~957–1007 (HTML form), ~354–573 (CSS), and ~1470–1584 (JS) —

Port it exactly — do not change the JS logic at all.
Only restyle the visual design to match the dark theme:
- Form background: rgba(255,255,255,0.04)
- Input fields: dark background, muted border, white text
- Labels: rgba(240,244,241,0.5)
- Calculate button: Kibi green, #0B0E0C text
- The boarding pass is already dark-themed — keep as-is, just verify it matches
- Error state: keep the red styling
- Loading spinner: adapt to dark theme
```

### STEP 7.3 [PROMPT → CLAUDE CODE]
```
Add the Eco section and Waitlist section:

Section: Eco Tracking (#eco)
  Background: slightly different dark shade: #0D1510
  Two-column layout (desktop) / stacked (mobile):

  Left column:
    Tag: "Environmental Impact"
    Title (Fraunces): "Your drive has an impact. Know it exactly."
    Sub: "Kibi uses EPA-certified data for your specific vehicle to calculate
          real CO₂ — not a national average. Every gallon. Every mile."
    3 bullet points:
      ● Tailpipe CO₂ per gallon from your actual vehicle model
      ● Lifetime CO₂ tracked across all trips
      ● Compare your footprint to flying the same route
    Note (italic, muted): "CO₂ formula: co2tailpipegpm × miles ÷ 1000. Source: EPA FuelEconomy.gov"

  Right column:
    2x2 grid of eco stat cards (same style as current site's eco-story-grid):
      🌳 "Offset with trees" — "Your trip = X trees worth of absorption / year"
      ✈️ "vs. Flying" — "X% less CO₂ than the same trip by plane"
      🍔 "In real terms" — "Your CO₂ = X hamburgers worth of emissions"
      📊 "vs. US Average" — "You're X% below the national daily average"

Section: Waitlist (#waitlist)
  Full-width, background: #0B0E0C with subtle radial green glow behind
  Center-aligned, max-width 600px, margin auto:

  Icon: <img src="Kibi_Logo_Icon_White.png" width="48">
  Title (Fraunces): "Be first on the road."
  Sub: "Kibi is live on iOS. Android and new features are coming.
        Drop your email and we'll let you know."

  Form: POST to https://formspree.io/f/[FORMSPREE_FORM_ID]
    Input: type="email" placeholder="your@email.com"
    Button: "Get Early Access →" (Kibi green)
    Hidden input: <input type="hidden" name="_subject" value="Kibi Waitlist Signup">

  Success state (show after submit, hide form):
    "✓ You're on the list. We'll be in touch."

  Proof strip below form:
    "Free to download  ·  No spam  ·  Unsubscribe anytime"
    (tiny, muted, DM Sans)
```

---

## ═══════════════════════════════════════════
## PHASE 8 — MOBILE LAYOUT
## ═══════════════════════════════════════════

### STEP 8.1 [PROMPT → CLAUDE CODE]
```
Add complete mobile responsive styles for ≤768px.

On mobile, the GSAP scroll experience must be completely disabled:
  - Add this JS check at the top of the GSAP init code:
    if (window.innerWidth <= 768) { return; } // skip all GSAP
  - The #road-scene should be position: relative (not fixed) on mobile
  - #scroll-experience height: auto (not 600vh) on mobile

Instead, on mobile show:
  - #road-scene as a static dark section (just the background gradient,
    no road layers, no scroll animations) — height: 100svh
  - Hero text centered, vertically centered in that space
  - App Store badge centered below

All post-scroll sections (how it works, calculator, features, eco, waitlist)
should be single-column stacked layout.

Specific mobile adjustments needed:
  - Nav: hamburger visible, desktop links hidden
  - Hero h1: font-size clamp(2.2rem, 8vw, 3rem)
  - Stats bar: 3 stats in a row (they fit at this size)
  - How It Works: 2 columns at 480px+, 1 column below that
  - Calculator: single column
  - Boarding pass: reduce padding, 2-column stats grid (already done in current site)
  - Feature cards: stack vertically
  - Eco: stack vertically
  - Waitlist form: stack input + button vertically
  - Footer: stack vertically

Test on: 390px wide (iPhone 15), 375px (older iPhones), 768px (iPad-ish).
```

### STEP 8.2 [MANUAL — mobile test]
```
1. Open Chrome DevTools → toggle device toolbar
2. Test at: 390px (iPhone 15 Pro), 375px, 768px, 480px
3. Check:
   [ ] No horizontal scrollbar at any width
   [ ] Hero text + App Store badge visible without scrolling
   [ ] No GSAP animations running (road scene is static)
   [ ] Calculator works (keyboard doesn't break layout)
   [ ] Hamburger menu opens and closes
   [ ] App Store badge tap target is ≥44px tall
4. CRITICAL: Test on actual iPhone in Safari
   Open your GitHub Pages URL on your iPhone
   Check that the hero is immediately visible and App Store badge is tappable
```

---

## ═══════════════════════════════════════════
## PHASE 9 — POLISH & DETAILS
## ═══════════════════════════════════════════

### STEP 9.1 [PROMPT → CLAUDE CODE]
```
Polish pass — apply these refinements:

1. Add a page-load animation: On first load, fade the entire page in from
   background color (avoid flash of unstyled content).
   Simple: body starts opacity 0, transitions to opacity 1 over 0.4s after DOMContentLoaded.

2. Nav scroll state: When user has scrolled past the immersive section
   (past 600vh), update the nav to show a subtle green bottom border:
   border-bottom: 1px solid rgba(46,189,122,0.2)

3. Scroll progress indicator: thin 2px line at very top of viewport,
   color: Kibi green, width goes from 0% to 100% as user scrolls
   through the 600vh scroll experience only (reset to nothing below it).

4. Add smooth reveal animations (IntersectionObserver) to all post-scroll
   section elements that don't already have them. Use the .reveal class
   pattern from WEBSITE_CONTEXT.md.

5. Cursor: On desktop, add a subtle custom cursor:
   A small dot (6px, Kibi green) that follows the mouse with a slight
   lag (CSS transition on a JS-tracked position). Keep it subtle — this
   is optional and should be removed if it feels gimmicky.

6. Footer: add the following links in small muted text:
   Privacy Policy (link to existing Notion privacy policy URL:
   https://empty-hedgehog-c4d.notion.site/Kibi-Privacy-Policy-31b455aa909e804ea731c062e28eaa2d)
   · Early Access
   · GitHub (link to your public repo)
   · © 2026 Kibi
```

### STEP 9.2 [PROMPT → CLAUDE CODE]
```
Performance and accessibility pass:

1. Add alt text to all images
2. Add aria-label to the hamburger button: "Open menu"
3. Add role="navigation" to <nav>
4. Ensure all text meets WCAG AA contrast ratios:
   - Body text on dark background: check rgba(240,244,241,0.45) — if it fails,
     increase opacity to 0.6
   - Green text on dark background: #2EBD7A on #0B0E0C — verify passes
5. Add <meta name="theme-color" content="#0B0E0C"> for mobile browser bar color
6. Add Open Graph meta tags for social sharing:
   <meta property="og:title" content="Kibi — Your Road Trip Co-Pilot">
   <meta property="og:description" content="Kibi finds the best exit every time — gas, food, and a clean bathroom at one stop.">
   <meta property="og:image" content="[YOUR_GITHUB_PAGES_URL]/og-image.png">
   Note: og:image needs a 1200x630 PNG — create this manually or skip for now
7. Ensure the App Store button has min-height: 44px for iOS tap targets
8. Add loading="lazy" to any images below the fold
```

---

## ═══════════════════════════════════════════
## PHASE 10 — FORMSPREE INTEGRATION & DEPLOY
## ═══════════════════════════════════════════

### STEP 10.1 [MANUAL — Formspree]
```
1. Log in to formspree.io
2. Get your form ID from Step 0.2
3. In index.html, find: action="https://formspree.io/f/[FORMSPREE_FORM_ID]"
4. Replace [FORMSPREE_FORM_ID] with your actual ID
5. Save and test: submit the form, check formspree.io dashboard
```

### STEP 10.2 [MANUAL — Deploy to GitHub Pages]
```
1. Commit index.html and all asset files to your GitHub repo:
   git add index.html appstore-badge.svg screenshot-setup.png screenshot-trip.png
   git add Kibi_Logo_Wordmark_White.png Kibi_Logo_Icon_White.png Kibi_Logo_Primary_White.png
   git commit -m "Website redesign: immersive scroll experience"
   git push origin main

2. Go to repo Settings → Pages
3. Confirm source is set to "Deploy from branch: main, / (root)"
4. Wait ~2 minutes, then visit your GitHub Pages URL

5. Test the live URL on:
   [ ] Desktop Chrome
   [ ] Desktop Safari
   [ ] iPhone (Safari) — MOST IMPORTANT
   [ ] Android Chrome (if available)
```

### STEP 10.3 [PROMPT → CLAUDE CODE — if scroll feels wrong after real deploy]
```
I've deployed the site to GitHub Pages and tested it on iOS Safari.
The following issues appeared: [DESCRIBE WHAT'S BROKEN]

Fix these issues. Common iOS Safari problems to watch for:
- GSAP ScrollTrigger behaves differently on iOS — ensure the `scrub` value
  is not too low (use scrub: 2 minimum on mobile)
- 100vh is problematic on iOS (browser chrome changes it) — replace all
  100vh in the scroll container with 100dvh or 100svh where supported
- Fixed positioning can fail on iOS with overflow:hidden on parent elements
  — ensure no parent of #road-scene has overflow:hidden on mobile
```

---

## ═══════════════════════════════════════════
## PHASE 11 — OPTIONAL ENHANCEMENTS (post-launch)
## ═══════════════════════════════════════════
# Do these AFTER the site is live and working. Not before.

### STEP 11.1 [OPTIONAL — Add sound toggle]
```
Add an optional ambient audio experience (engine hum / road wind):
1. Source a royalty-free highway ambient audio file (~10 seconds, loops)
2. Add a muted audio element with loop
3. Add a small speaker icon in bottom-left corner: 🔇/🔊
4. On click, toggle audio on/off
5. Default: muted. Never autoplay unmuted.
6. Show a "🔊 Turn on audio for full experience" hint in the hero that fades after 3s

Note: This is optional and low-priority. Ship without it first.
```

### STEP 11.2 [OPTIONAL — Smooth scrollbar]
```
Consider replacing the native scrollbar with a custom one for the immersive section.
Library option: Lenis (lightweight smooth scroll, no license issues)
CDN: https://cdn.jsdelivr.net/npm/lenis/dist/lenis.min.js

This makes the scroll feel silkier but adds complexity.
Only do this if the native scroll feels jerky.
```

### STEP 11.3 [OPTIONAL — Custom domain]
```
When you get your custom domain (e.g. kibi.app or getkibi.com):
1. Add a CNAME file to your repo root with your domain
2. Update GitHub Pages settings to use custom domain
3. Enable "Enforce HTTPS"
4. Update the og:image URL in meta tags
5. Update the privacy policy URL in footer to your GitHub Pages version
   (reminder from CONTEXT.md: migrate privacy policy off Notion before App Store submission)
```

### STEP 11.4 [OPTIONAL — Analytics]
```
To add privacy-respecting analytics (no cookie banner needed):
Recommended: Plausible Analytics (paid, $9/mo) or Umami (free, self-hosted)
Avoid Google Analytics (requires cookie consent banner — clutters the experience).

Add the script snippet to <head> once you have an account.
Track these events:
- App Store badge click
- Waitlist form submission
- Calculator run
- Time on page / scroll depth (built-in with Plausible)
```

---

## ═══════════════════════════════════════════
## QUICK REFERENCE — GSAP SCROLL PERCENTAGES
## ═══════════════════════════════════════════

When scenes feel off, this is the cheat sheet for adjusting timing:

```
Scene 1 (Parallax enter):    0%  – 15%
Scene 2 (Dashboard):        15%  – 35%
Scene 3 (Speed up):         35%  – 50%
Scene 4 (Exit sign):        50%  – 62%
Scene 5 (Billboard 1):      62%  – 70%
Scene 6 (Billboard 2):      70%  – 78%
Scene 7 (Billboard 3, eco): 78%  – 85%
Scene 8 (Exit ramp):        85%  – 92%
Scene 9 (Final CTA):        92%  – 100%

Total scroll height: 600vh
Each 1% of scroll ≈ 6vh of scrolling
```

To adjust scene timing, change these values in the GSAP timeline.
To make a scene last longer, widen its percentage range and narrow adjacent scenes.

---

## EMERGENCY FIX PROMPTS

### If GSAP animations aren't triggering:
```
The GSAP ScrollTrigger animations in index.html are not triggering on scroll.
The #scroll-experience section is 600vh tall. The #road-scene is position: fixed.
Debug and fix the ScrollTrigger setup. Check: is ScrollTrigger registered?
Are element IDs correct? Is the trigger element in the DOM when JS runs?
Wrap everything in window.addEventListener('load', ...) if not already done.
```

### If the site is broken on mobile:
```
The site breaks on mobile (≤768px). The GSAP scroll experience should be
completely disabled on mobile — check that the window.innerWidth guard
is working. On mobile, the layout should be a simple single-column dark
site with static background. Fix all mobile layout issues.
```

### If the boarding pass calculator is broken:
```
The road trip calculator in the new dark-themed index.html is broken.
The original working version is in index_OLD.html.
Compare the JS logic in both files and restore the working version without
changing the dark visual styling we've already applied.
```
