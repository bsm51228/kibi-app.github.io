# Known Issues

Tracked issues that are known but deferred. Each entry: ID, title, discovery date, behavior, why deferred, fix sketch.

## KI-02 — Related-routes scorer produces weak matches for geographically isolated routes

**Discovered:** 2026-04-16 during 20-route batch generation

**Behavior:** When a route shares zero highway tokens and zero endpoints with any other route in the catalog (e.g., `los-angeles-to-las-vegas` shares nothing with any east-of-Mississippi route), `scripts/build-routes.js::buildRelatedRoutes` falls back to the alphabetical tiebreaker among score-0 candidates. This produces irrelevant matches like `athens-to-atlanta` at position #3 of LA→Vegas's related-routes section.

**Why deferred:** Edge case affecting a small number of routes. Self-resolves as route density grows — at 60+ routes, meaningful-overlap candidates exist for every route.

**Fix:** Add a region/state-distance fallback to the scorer when primary token-overlap score is 0 for all candidates. Implement if/when the issue persists at 60+ routes.
