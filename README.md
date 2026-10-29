# BVG Departure Board — Icinga bottom-left widget (preview)

A small, dependency-free preview of the departure widget for the Icinga TV display.

## Files

```
departure-board/               ← repo root
├── 01_Project/                ← site code (what gets served/deployed)
│   ├── index.html             — dark "Icinga-style" stand-in dashboard with the widget embedded via iframe, pinned to the bottom-left corner.
│   └── departures.html        — the actual widget: one S-Bahn station and one U-Bahn station, next departures for both directions each, live from the [BVG transport.rest API](https://v6.bvg.transport.rest/).
├── 02_Design/DESIGN.md        — Berlin S-Bahn/U-Bahn design and iconography reference.
├── 03_Screenshots/            — verified preview screenshots.
└── docs/PROJECT_LOG.md        — project log (goal, status, session history).
```

## Run locally (Mac)

```bash
cd departure-board
python3 -m http.server 8000 --directory 01_Project
```

Then open http://localhost:8000/

(The API is CORS-enabled, so double-clicking `01_Project/index.html` also works — no server needed.)

## Configuration

Two ways to configure — no file editing needed either way:

1. **Built-in setup panel**: click the `setup` button in the widget footer, pick stations, Save. Stored in the browser's localStorage (per browser/per device), so on the NUC you configure once and it persists across reboots. Reset returns to defaults.
2. **URL parameters** on `departures.html` (or the iframe `src` in `index.html`) — these override the saved panel config when present.

Values may be BVG IBNR stop ids (digits) or plain station names — names are resolved automatically via `/stops?query=`.

| Param | Meaning | Default |
|-------|---------|---------|
| `s`   | S-Bahn stop (id or name) | `S Humboldthain` |
| `u`   | U-Bahn stop (id or name) | `U Voltastraße` |
| `r`   | Regional stops to cycle through (comma-separated) | `S+U Gesundbrunnen,S+U Alexanderplatz` |
| `n`   | Departures per direction  | `2` |

Example: `departures.html?s=900100003&u=900100053&n=3`

The third block (red `RE` badge) shows regional trains (RE/RB/IC/ICE) and
alternates between the configured `r` stops every 20 seconds — useful while
the Stadtbahn regional platforms (Alexanderplatz) are under construction
and traffic shifts to Gesundbrunnen.

## Behavior

- Refreshes every 30 seconds.
- Shows minutes until departure (`now`, `3 min`, ...); absolute time with `*` if more than 60 minutes out.
- Shows delay as `+2` in orange next to the time.
- Departures are grouped per direction (terminus) — up to 2 directions, e.g. eastbound + westbound.

## Deploying to the NUC

The NUC does not get a copy of this repo. It gets a folder with exactly one file:

```
departure-widget/
└── departures.html    ← copied from 01_Project/ — fully self-contained (no CSS/JS/font files)
```

Serve it with any static server on the NUC, e.g. (Windows, Python installed):

```bat
python -m http.server 8000 --directory C:\departure-widget
```

Requirements:

- The NUC needs internet access to `https://v6.bvg.transport.rest` (the only external dependency).
- Station configuration goes in the iframe URL, not the file — so keep the file unmodified for easy updates (just overwrite it when the widget changes).

## Embedding in the real Icinga page

In your Icinga source, add the same fixed-position iframe pointing at the NUC folder's served URL (localhost is fine since the NUC's Chrome opens the Icinga page directly):

```html
<iframe src="http://localhost:8000/departures.html"
        style="position: fixed; left: 16px; bottom: 16px; width: 340px; height: 300px;
               border: 0; background: transparent;"
        scrolling="no"></iframe>
```

## Notes

- The widget sets `background: transparent` on `body` so it blends into the Icinga page; for a standalone look, give `.widget` your desired backdrop in `departures.html`.
- Height ~300px fits two stations with 2 departures each. Adjust `n` and the iframe height if you change that.
