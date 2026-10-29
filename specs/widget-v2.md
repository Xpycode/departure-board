# Departure Widget v2 — Readability & Resilience Specification

**Status:** Complete (implemented; TV-distance verification pending)
**Created:** 2026-10-29
**Last Updated:** 2026-10-29

---

## Problem Statement

### What problem does this solve?

The widget works, but at TV distance it is hard to act on, and it is not yet dependable for 24/7
unattended display:

- Platform/track is invisible — the most actionable field when a regional train is due.
- Nothing marks the train you can actually still catch; every row looks equally urgent.
- A cancelled train renders like a normal departure (falls back to planned time) — misleading.
- One failed fetch visibly breaks a block; a longer API outage leaves an ambiguous screen.
- Long-lived dashboard tabs are a documented memory-leak/crash risk; nothing recovers them.
- The S-Bahn green badge fails WCAG AA contrast (4.28:1); readability at TV distance is unverified.

Smallest worthwhile outcome: a glanceable board where, from across the room, the eye lands on
the catchable train, its platform, and a trustworthy freshness signal — and that survives
network hiccups and browser decay without manual attention.

### Who has this problem?

One household: the TV/NUC Icinga display in daily use, read from several meters away, running
unattended for long stretches.

### How they solve it today?

The v1 widget (sessions 1–23) shows lines, directions, countdowns and delays. Missing platforms,
catchability, cancellation state and offline behavior; freshness is only an `updated HH:MM:SS`
stamp that a distant viewer cannot interpret as healthy or degraded.

---

## Proposed Solution

### One-Liner

Make the existing three-block widget actionable at TV distance (platforms, catchable-train
highlight, cancellation state, header clock) and dependable 24/7 (last-good data with a status
indicator, scheduled self-reload, parent-page heartbeat watchdog).

### Key Capabilities

1. **Platform column** — track/Gleis number per departure, right-aligned fixed-width column
   between direction and countdown; trimmed to the leading number (`"1 (U8)"` → `1`).
2. **Catchable-train highlight** — per block and direction, the first departure that clears the
   station's lead time gets a left accent bar (warn orange, ~3 px), bold text, and a `»` marker;
   later rows dim toward `--dim`. Highlight is luminance/weight-based, not hue-based.
3. **Cancellation rendering** — departures whose remarks contain
   `text.realtime.journey.cancelled` (today: `when === null` with cancel status) render
   struck-through and dimmed, are excluded from the catchable highlight, and show a small
   "fällt aus" tag instead of a countdown.
4. **Platform-change emphasis** — when `platform` differs from `plannedPlatform` (or the
   `text.realtime.stop.dep.platformChange` status remark is present), the platform is shown in
   warn orange so a changed track stands out.
5. **Hint icons** — small monochrome inline SVG glyphs after the direction text for mapped remark
   hints; v2 maps only `FK` ("Bicycle conveyance") and `gy` (bike-scheme train) to a bicycle icon.
   Unmapped hints are ignored. Max two icons per row; `title` attribute carries the meaning.
6. **Clock/date header** — one top bar: `HH:MM` large, weekday + date small, right-aligned;
   ticked every second by updating only the text node.
7. **Offline/stale handling** — keep the last-good response per block in memory; on fetch
   failure render last-good data dimmed (~50% opacity) with a banner "Offline — times as of
   HH:MM". A status dot beside the existing stamp: green = live, amber = a failed refresh in
   the current cycle, red = last good data older than 15 min. Never blank a block on error.
8. **Scheduled self-reload** — the widget reloads itself every 4 hours (heap reset; config
   survives in localStorage/URL params).
9. **Parent heartbeat watchdog** — README gains a listener snippet: if no
   `bvg-widget-size` message for ~3 minutes, set `iframe.src = iframe.src` to force a reload.
   The widget sends its size message at least once per 30 s refresh even when unchanged.
10. **Contrast fix** — darken the S badge green (`#008d4b` → `#007a41`) or otherwise lift
    white-on-badge contrast above 4.5:1; README recommends `scale` 1.5 for TV distance
    (≥ ~16 px minimum text at ~3 m per signage guidance).

### User Flow

1. Source/input: same live BVG API fetches as today (no new endpoints, no new request rate
   class; still ~7 req/min, limit is 100/min).
2. User action: none — configuration unchanged; `scale` recommendation for TV documented.
3. Destination/output: same fixed bottom-right iframe in the Icinga page.
4. Observable outcome: from the couch, the viewer sees which train they can catch, from which
   platform, whether it is cancelled, and whether the data is live or stale.

### Usefulness or Feasibility Check

- Uncertainty: none material — every capability was verified live against the API
  (platform presence 100% across all five stops; FK hint confirmed; platform changes observed
  at all three RE stops; cancel status remarks observed) and against display conventions
  (DAISY, National Rail, GTFS staleness thresholds, WCAG).
- Agreed limit: this spec; implementation via a follow-up plan.
- Stop/replan: if the U8 `occupancy` field or hint semantics drift (both undocumented), drop
  the affected display rather than repairing it against the public instance.

---

## Acceptance Criteria

> Given/When/Then per `56_acceptance-criteria.md`. Verified on the Mac preview; TV verification
> remains the existing open item.

### Core Functionality

- [ ] Given a departure with `platform` set, when the block renders, then the platform number
      appears in a fixed-width right-aligned column, trimmed to the leading number.
- [ ] Given a departure with `platform: null` but `plannedPlatform` set, when rendered, then the
      planned platform is shown with no emphasis.
- [ ] Given a departure where `platform` differs from `plannedPlatform`, when rendered, then the
      actual platform is shown in warn orange.
- [ ] Given a block with at least one departure clearing its lead time, when rendered, then
      exactly one row per direction carries accent bar + bold + `»`, and no row that leaves
      sooner than the lead time is highlighted.
- [ ] Given a cancelled departure, when rendered, then the row is struck-through, dimmed, shows
      "fällt aus" instead of a countdown, and is never highlighted as catchable.
- [ ] Given a departure with an `FK` or `gy` hint remark, when rendered, then a bicycle icon
      appears after the direction text with a `title` describing it.
- [ ] Given the widget is running, when one second passes, then the header clock advances
      without rebuilding the surrounding DOM (no leak-inducing re-render).
- [ ] Given the widget renders, when it reports its size to the parent, then the report fires
      at least once every 30 s cycle regardless of size change (heartbeat requirement).

### Edge Cases

- [ ] Given the first fetch after reload fails, when the block would render, then the block shows
      the block's standard empty/error state — there is no last-good data yet.
- [ ] Given stale data older than 15 min, when rendering, then the status dot is red and the
      banner names the age of the data.
- [ ] Given a fetch fails for one block but succeeds for others, when rendering, then only the
      failed block is dimmed; the others render normally.
- [ ] Given the RE rotation switches stations during an outage, when the next slot arrives, then
      the incoming station's stale banner reflects its own last-good age (no cross-block
      contamination of last-good caches).
- [ ] Given more than two hint icons would render on one row, when rendering, then only the
      first two appear.
- [ ] Given an unmapped hint code, when rendering, then nothing extra appears.

### Error States

- [ ] Given an API 404/500 or network error, when a block refreshes, then the previous good data
      stays on screen dimmed with an "Offline — times as of HH:MM" banner; the block is never
      blanked by a transient error.
- [ ] Given the widget has been up 4 hours, when the timer fires, then the page reloads itself
      and returns to an identical state (config from URL/localStorage).
- [ ] Given the widget's iframe has stopped sending size messages for 3 minutes, when the
      parent listener notices, then the parent forces an iframe reload.

---

## Technical Considerations

### Dependencies

- None new. Same single-file, dependency-free constraint; sole external dependency remains
  `v6.bvg.transport.rest` (CORS-enabled, cache-control `max-age=30`).
- No new endpoints required; journeys/occupancy explicitly deferred (see Out of Scope).

### Architecture Notes

- Platform fallback chain: `platform` ?? `plannedPlatform` ?? omit (column width stable).
- Platform-change detection: prefer the `text.realtime.stop.dep.platformChange` status remark
  when present; fall back to `platform !== plannedPlatform`.
- Cancellation detection: status remark codes (`text.realtime.journey.cancelled`,
  `text.realtime.stop.cancelled`), not `when === null` alone (session 7 already treats
  `when: null` as "fall back to planned time" for non-cancelled cases).
- Last-good cache: in-memory per block (per cycling RE station), keyed to the block config;
  no localStorage persistence needed — a reload intentionally starts fresh.
- Heartbeat: extend the existing `bvg-widget-size` postMessage (add a lightweight heartbeat
  message or guarantee a size report per cycle) so the documented parent listener can double
  as watchdog.
- Scheduled reload: `setTimeout(location.reload, 4 * 3600 * 1000)`; timer starts on load.
- Hint mapping is a fixed table (code → icon) in the file; unmapped codes ignored by design.

### Performance

- Fetch rate unchanged (~7 req/min vs 100/min limit); no new requests in v2.
- Clock must not trigger the existing MutationObserver size reporting or ticker rebuilds
  (session 18 deduped size reports; keep it that way).

### Security

- No auth, no secrets, no user input beyond existing station config; remark HTML continues to
  be flattened via `stripHtml` (never innerHTML raw remark text); hint icons are hardcoded SVG.

---

## Out of Scope

Explicitly excluded from this spec:

- **Bus/night-bus block** — a fourth block pushes iframe height past ~380 px at scale 1; no bus
  stop has been chosen. Revisit after TV verification.
- **Journeys "leave now, arrive by" line** — `/journeys` is verified to work (S1/S3 connection
  Humboldthain → Ostbahnhof in ~17 min, ~+2 req/30 s) but does not fit the corner-widget shape;
  park until there is a concrete origin→destination pair worth showing.
- **Occupancy/load display** — field exists only on U8 departures, is absent from api.html, and
  could disappear without notice. Not built on undocumented API behavior.
- **Blinking imminent-departure rows** (DAISY-style) — catchable trains here are 8–12 min out;
  blinking at TV distance adds noise without actionable value.
- **Screen burn-in mitigation beyond existing variation** — LCD assumed; the clock and RE
  rotation already vary pixels.
- **Automatic station rotation reversion after 12 Dec 2026** — manual config change, per the
  logged open item.

---

## Open Questions

| Question | Status | Answer |
|----------|--------|--------|
| Highlight styling: accent bar + `»` acceptable, or prefer BVG-style treatment? | Resolved | Accent bar + bold + `»` (default accepted by user) |
| Scheduled reload interval: 4 h proposed; 12 h also defensible | Resolved | 4 h (default accepted by user) |
| S badge contrast fix: darker green (`#007a41`) vs heavier text? | Resolved | Darker green `#007a41` (default accepted by user) |
| Heartbeat: reuse `bvg-widget-size` guaranteed-per-cycle vs new dedicated message type? | Resolved | Guaranteed `bvg-widget-size` report once per 30 s cycle (default accepted by user) |
| Should the header clock show seconds? (more change = more burn-in variation, less calm) | Resolved | No seconds — `HH:MM` (default accepted by user) |
| "fällt aus" tag wording (German) vs "cancelled" (English)? | Resolved | German "fällt aus" (default accepted by user) |

---

## Related

- Research sources: agent findings of 2026-10-29 (live API verification: platform presence,
  hint catalog, cancel/platform-change status codes, journeys shape, rate limits, error
  behavior; display conventions: DAISY, National Rail boards, GTFS 15-min staleness threshold,
  Grafana/kiosk tab-crash reports, WCAG contrast measurements of the current palette).
- Project log: `docs/PROJECT_LOG.md` sessions 1–23.
- Design language: `02_Design/DESIGN.md`.
