// ==UserScript==
// @name         Icinga BVG Departure Widget (bottom-left)
// @namespace    https://github.com/Xpycode/departure-board
// @version      1.0.0
// @description  Shows BVG S-/U-Bahn departures in the bottom-left corner of the Icinga Web 2 monitoring page. Config lives in WIDGET_URL (station selection, scale, api base) — see the repo README for all parameters.
// @match        http://*/*
// @match        https://*/*
// @run-at       document-end
// @noframes
// @grant        none
// ==/UserScript==

(function () {
  "use strict";

  // --- configuration -------------------------------------------------------
  // Adjust to your setup:
  //  - NUC serving the widget locally:  http://localhost:8000/departures.html
  //  - shared internal server:          http://<internal-host>:8000/departures.html?api=/api
  // Station/lead-time/scale parameters go into this URL (README: "Configuration").
  var WIDGET_URL = "http://localhost:8000/departures.html";

  var OFFSET = 16;         // px distance from the viewport edges
  var INITIAL_W = 340;     // placeholder size; auto-fit adjusts it
  var INITIAL_H = 300;
  var WATCHDOG_MS = 3 * 60 * 1000;  // no size heartbeat = hung = reload

  // Run only on the Icinga Web 2 pages shown on the TV (the businessprocess
  // views and the dashboard). Broad @match above; narrow it here.
  if (!/\/icingaweb2\//.test(location.pathname)) return;
  // Keep the widget out of popups/modals, only on the top document window.
  try { if (window.top !== window.self) return; } catch (e) { return; }

  // --- iframe --------------------------------------------------------------
  var frame = document.createElement("iframe");
  frame.id = "bvg-widget";
  frame.src = WIDGET_URL;
  frame.title = "BVG departures";
  frame.setAttribute("scrolling", "no");
  frame.setAttribute("aria-hidden", "true");
  frame.setAttribute("tabindex", "-1");
  Object.assign(frame.style, {
    position: "fixed",
    left: OFFSET + "px",
    bottom: OFFSET + "px",
    width: INITIAL_W + "px",
    height: INITIAL_H + "px",
    border: "0",
    background: "transparent",
    zIndex: "99999",
    pointerEvents: "auto"
  });

  // --- auto-fit + heartbeat watchdog ----------------------------------------
  var lastBeat = Date.now();
  window.addEventListener("message", function (e) {
    if (e.data && e.data.type === "bvg-widget-size") {
      lastBeat = Date.now();
      var f = ensure();
      if (!f) return;
      f.style.width = e.data.width + "px";
      f.style.height = e.data.height + "px";
    }
  });

  setInterval(function () {
    var f = ensure();
    if (!f) return;
    if (Date.now() - lastBeat > WATCHDOG_MS) {
      f.src = f.src;
      lastBeat = Date.now();
    }
  }, 30000);

  // --- survive Icinga's AJAX rewrites ---------------------------------------
  // Icinga replaces whole containers on auto-refresh; if anything removes or
  // restyles the iframe, (re)attach it to <body>.
  function ensure() {
    var f = document.getElementById("bvg-widget");
    if (f && f.parentElement === document.body) return f;
    if (f) f.remove();
    if (document.body) {
      document.body.appendChild(frame);
      return frame;
    }
    return null;
  }

  if (document.body) ensure();
})();
