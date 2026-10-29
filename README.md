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
├── 04_Internal/server.py      — optional internal server: hosts the widget and caches API calls for shared use.
├── 05_Integration/            — the real Icinga Web 2 integration: Tampermonkey userscript for the NUC's Chrome.
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
| `sl`  | S lead time (min walk — hides trains leaving sooner) | `8` |
| `u`   | U-Bahn stop (id or name) | `U Voltastraße` |
| `ul`  | U lead time (min walk — hides trains leaving sooner) | `12` |
| `r`   | Regional stops to cycle through (comma-separated) | `S+U Gesundbrunnen,S Charlottenburg,S Ostbahnhof` |
| `rl`  | RE lead time in minutes (one per station, comma-sep.) — hides trains leaving sooner than the walk to that station | `10` |
| `rf`  | Only these RE lines (comma-separated, substring match, empty = all) | — |
| `n`   | Departures per direction  | `2` |
| `api` | BVG API base URL — point at a caching proxy for shared/internal use; relative URLs work same-origin (`/api` when served by the internal server) | `https://v6.bvg.transport.rest` |
| `scale` | Display scale (0.8–2) — makes everything in the widget proportionally larger/smaller | `1` |
| `ts` | Info line text size (px, 8–18) | `12` |

Example: `departures.html?s=900100003&u=900100053&n=3`

The third block (red `RE` badge) shows regional trains (RE/RB/IC/ICE) and
alternates between the configured `r` stops every 20 seconds. The default
rotation is Gesundbrunnen (north ring, where regional traffic shifted during
the construction), plus Charlottenburg and Ostbahnhof, where the RE/RB lines
terminate while the Stadtbahn is closed to regional traffic (14 June –
12 December 2026); after 12 December, consider adding back
S+U Alexanderplatz. A countdown in the RE header shows the
next station and the seconds until the switch; every configured station
gets its slot in turn. A station with no departures in the 4-hour window
shows that honestly for its slot instead of being skipped.

## Behavior

- Refreshes every 60 seconds (regional trains barely move faster); S/U blocks look 30 minutes ahead, the RE block 4 hours (regional service is sparse — a shorter window is often empty).
- The API filters products only by exclusion (`suburban=false&bus=false&...`); the widget builds those queries per block.
- Shows minutes until departure (`now`, `3 min`, ...) plus the absolute departure time in small dim text (`8 min 18:24`), so it can be cross-checked against the clock header. Beyond 60 minutes only the absolute time is shown (`19:22 *`).
- Shows delay as `+2` in orange next to the time.
- Shows the platform/track in a fixed column (realtime platform, falling back to the planned one). A platform that changed vs. plan is shown in orange.
- The first still-catchable departure per direction (one that clears the lead time) is highlighted: orange accent bar, bold, `»` marker. Later departures are dimmed.
- Cancelled trains are shown struck-through with "fällt aus" instead of a countdown, and are never highlighted as catchable.
- A bicycle icon after the direction marks trains with confirmed bicycle conveyance (API `FK`/`gy` hints; hover for the exact remark).
- Clock/date header (top right, no seconds — calmer at TV distance).
- Departures are grouped per direction (terminus) — up to 2 directions, e.g. eastbound + westbound.
- Offline resilience: each block keeps its last good data; if a refresh fails, that data stays on screen dimmed with an "Offline — times as of HH:MM" banner. A status dot next to the footer timestamp shows green (live), amber (a block failed this cycle) or red (no good data for 15+ minutes). Blocks are never blanked by transient errors.
- 24/7 resilience: the widget reloads itself every 4 hours (config survives in URL params and localStorage), and sends a size message on every refresh cycle so the embedding page can detect a hung iframe (see the watchdog snippet below).
- Info line: disruption warnings of the displayed trains (API "warning" remarks, e.g. line cancellations or construction replacements) rotate one at a time in a yellow line above the footer, with a position counter. Click the counter to jump to the next message, click the text to cycle scroll speed (1x → 2x → 4x); a completed scroll pass auto-advances. Hidden when there are none. HTML in remark texts (some are bare links) is flattened to `label: URL`. Text size is the `ts` setting.

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

## Sharing internally (with a cache)

If several colleagues' screens should run the widget, don't let every instance call the public API directly. Run one shared instance of `04_Internal/server.py` on an internal host (or subdomain): it serves the widget files and proxies the API behind a 30-second in-memory cache, so N screens generate at most one upstream request per endpoint and window — and everyone shares the same cache.

```bash
# one-time: copy server.py, departures.html (and optionally index.html) into one folder
python3 server.py 8000
```

Colleagues then embed:

```html
<iframe id="bvg-widget" src="http://<internal-host>:8000/departures.html?api=/api" ...></iframe>
```

(`api=/api` is a relative URL — the widget then fetches through the same origin's proxy. It is also a setup-panel field.)

Details:

- **No dependencies** beyond Python's standard library; the cache is in-memory (resets on restart, which is fine at this TTL).
- **Stale-while-error**: expired entries are kept and served when the public API is unreachable — short outages degrade to slightly old data (`X-Cache-Status: STALE`) instead of errors. The widget's own offline indicator still shows the state honestly.
- `X-Cache-Status` response header (`MISS` / `HIT` / `STALE`) lets you check the cache is working: `curl -sI "http://localhost:8000/api/stops?query=Humboldthain" | grep X-Cache`.
- If you'd rather use an existing reverse proxy: an nginx location with `proxy_pass https://v6.bvg.transport.rest/;` and `proxy_cache_valid 200 30s;` gives the same effect; set the widget's `api` param to that location.

Footprint per widget instance: about 6 API calls per minute (2 refreshes × 3 blocks), well under the public instance's 100 requests/minute limit — and with the shared cache, upstream traffic grows with the *number of distinct station configurations*, not the number of screens.

## Embedding in the real Icinga page

The TV NUC runs Chrome against the real Icinga Web 2 page (`/icingaweb2/…`, businessprocess views with 1-second auto-refresh over AJAX). Two ways to add the widget — the userscript is the recommended one, since Icinga Web 2 has no per-page HTML hook and rewrites its containers on every auto-refresh.

### Option A — Tampermonkey userscript (recommended for the NUC)

Install the [Tampermonkey](https://www.tampermonkey.net/) extension in the NUC's Chrome, create a new script, and paste the contents of [`05_Integration/icinga-departures.user.js`](05_Integration/icinga-departures.user.js). Then set the `WIDGET_URL` constant inside to wherever the widget is served — for the NUC's local server the default `http://localhost:8000/departures.html` already fits; for the shared internal server use `http://<internal-host>:8000/departures.html?api=/api`. Any station/scale parameters (README: "Configuration") go into the same URL.

What the userscript handles:

- Pins the iframe to the **bottom-left** corner, above all Icinga content.
- Only activates on `/icingaweb2/` pages in the top document window (no popups/modals).
- Survives Icinga's AJAX auto-refresh: if anything removes or restyles the frame, it is re-attached to `<body>`.
- Auto-fits the frame to the widget's reported size (`bvg-widget-size` postMessage) and force-reloads the iframe when the heartbeat stops for 3 minutes.

### Option B — edit the Icinga layout directly

If you can edit the server (e.g. a custom module or `public/` overlay), add the same fixed-position iframe plus the listener script to the page layout:

```html
<iframe id="bvg-widget" src="http://localhost:8000/departures.html"
        style="position: fixed; left: 16px; bottom: 16px; width: 340px; height: 300px;
               border: 0; background: transparent;"
        scrolling="no"></iframe>
```

The widget reports its rendered size after every refresh via `postMessage` (type `bvg-widget-size`, with `width`/`height`) — at least once per 60-second cycle even when the size is unchanged, so the messages double as a heartbeat. To make the iframe auto-fit (recommended — it also tracks the display scale and any station changes) and recover a hung widget, add this listener to the parent page:

```html
<script>
  var lastBeat = Date.now();
  window.addEventListener("message", function (e) {
    if (e.data && e.data.type === "bvg-widget-size") {
      lastBeat = Date.now();
      var f = document.getElementById("bvg-widget");
      f.style.width = e.data.width + "px";
      f.style.height = e.data.height + "px";
    }
  });
  // Watchdog: no heartbeat for 3 minutes = force-reload the widget iframe.
  setInterval(function () {
    if (Date.now() - lastBeat > 3 * 60 * 1000) {
      var f = document.getElementById("bvg-widget");
      f.src = f.src;
      lastBeat = Date.now();
    }
  }, 30000);
</script>
```

(give the iframe `id="bvg-widget"`). Alternatively size it manually: `width = 340 × scale`, with enough height for all three station blocks plus footer — roughly `320 × scale` with 2 departures per direction, more if you raise `n`.

## Notes

- For TV viewing at ~3 m distance, signage guidance puts the minimum readable text at roughly 16 px; at the widget's default scale (13 px rows) that means `scale=1.5` on the NUC is a good starting point. The auto-fit listener handles the resulting larger frame automatically.
- The widget sets `background: transparent` on `body` so it blends into the Icinga page; for a standalone look, give `.widget` your desired backdrop in `departures.html`.
- Height ~300px fits two stations with 2 departures each; the full three-block widget (S, U, RE) plus clock and info line needs roughly 360px at scale 1. Use the auto-fit listener or adjust the iframe height if you change `n` or `scale`.
