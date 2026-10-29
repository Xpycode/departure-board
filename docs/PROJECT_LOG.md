# Project Log

## Goal

A small website that can be framed into the Icinga monitoring page (displayed on a TV via Chrome on a Windows NUC) to show the next departures of Berlin S-Bahn and U-Bahn stations in the bottom-left corner — at most one S-Bahn station and one U-Bahn station, for both directions each.

## Status

**Preview complete and verified on local Mac** (2026-10-29):

![Preview running with live BVG data](../03_Screenshots/docs-preview.png)

Screenshot shows the Icinga stand-in dashboard with the widget pinned bottom-left, rendering real departures for S+U Alexanderplatz (S9, S3, U2, with "now"/"1 min"/"3 min" countdowns and delays).

## What was built

| File | Purpose |
|------|---------|
| `01_Project/index.html` | Dark Icinga-style stand-in dashboard (host/service cards, live clock) with the widget embedded as a fixed-position iframe, bottom-left. |
| `01_Project/departures.html` | The actual widget: one S-Bahn + one U-Bahn station, next departures for both directions (grouped by terminus), line badges, countdown, delay display (`+2` in orange). Auto-refresh every 30s. |
| `02_Design/DESIGN.md` | Berlin S-Bahn/U-Bahn design and iconography reference. |
| `03_Screenshots/docs-preview.png` | Verified screenshot of the running preview. |
| `README.md` | Run instructions, configuration reference, and the iframe embed snippet for the real Icinga page. |

## Technical decisions

- **Data source**: [BVG transport.rest API](https://v6.bvg.transport.rest/) (`v6.bvg.transport.rest`), a free public instance — no API key needed, CORS-enabled, so it works from `file://` too.
  - Departures: `GET /stops/{id}/departures?results=20&suburban=true|subway=true`
  - Stop search: `GET /stops?query={name}`
  - Stop ids are BVG IBNRs (e.g. `900100003` = S+U Alexanderplatz; the `de:11000:...` form is NOT accepted by the departures endpoint — "id must be an IBNR").
- **No dependencies, no build step**: plain HTML/CSS/JS, single files. Deliberate, since the final target is a TV display that should never break.
- **Iframe embedding**: the widget is a separate document so it can be dropped into any parent page (Icinga) with one `<iframe>` tag and zero interference with the parent's CSS/JS.
- **Direction grouping**: departures are grouped by the `direction` field (terminus), up to 2 directions shown, N departures each (default 2).

## Configuration

URL params on `departures.html`: `?s={S-Bahn stop IBNR}&u={U-Bahn stop IBNR}&n={departures per direction}`. Defaults: Alexanderplatz for both, n=2.

## Open items

- [x] Decide final stations — S Humboldthain, U Voltastraße, plus a regional block alternating Gesundbrunnen/Alexanderplatz (done, session 4).
- [ ] Integrate the iframe snippet into the real Icinga page source (user will provide the source code later — session hand-off point, continue via CLI).
- [ ] Verify rendering on the TV/NUC (Chrome on Windows) — especially readability at TV distance; may need a font-size scale config option.
- [ ] Position moved to bottom-right (user correction in session 4) — update `index.html` stand-in accordingly when integrating.
- [ ] NUC deployment: the NUC gets its own folder with only `01_Project/departures.html` (self-contained single file), not a copy of this repo; serve via a local static server, config stays in the iframe URL.

## Session history

1. **2026-10-29 (session 1)** — Built the preview (`index.html`, `departures.html`, `README.md`) against the live BVG API; verified API response shape via `v6.bvg.transport.rest`; JS syntax-checked with `node --check`. Repo did not exist yet.
2. **2026-10-29 (session 2)** — User created private repo `Xpycode/departure-board` via `gh repo create`; pushed initial commit `805ee85` to `main` with the three files. User confirmed the preview runs locally with live data (screenshot provided → `docs-preview.png`).
3. **2026-10-29 (session 3)** — Added this log (`PROJECT_LOG.md`) and the verified screenshot.
4. **2026-10-29 (session 4)** — New station defaults (S Humboldthain, U Voltastraße); added third "RE" block for regional trains cycling between S+U Gesundbrunnen and S+U Alexanderplatz every 20s (Stadtbahn RE construction); stop params now accept names or IBNRs (auto-resolved via `/stops?query=`); user clarified widget position is bottom-right. JS syntax-checked with `node --check`.
5. **2026-10-29 (session 5)** — Merged the two remote `vibe/*` branches (regional block, design reference) into `main` locally and pushed; BVG API endpoints re-verified live. Restructured the repo to the standard numbered folder layout: site code into `01_Project/`, design reference into `02_Design/`, screenshot into `03_Screenshots/`, this log into `docs/`; added `.gitignore`; README updated for the new paths.
6. **2026-10-29 (session 6)** — Deployment decision: the NUC will get a standalone folder with only `departures.html` (verified self-contained: no local asset references, sole runtime dependency is the BVG API), not a copy of this repo. README gained a "Deploying to the NUC" section; config stays in the iframe URL so the file can be updated by overwrite.
