#!/usr/bin/env python3
"""Internal departure-board server: widget hosting + shared BVG API cache.

Serves the widget (departures.html) and proxies the BVG transport.rest API
behind an in-memory cache, so many widget instances (one per colleague's
screen) produce at most one upstream request per endpoint and cache window.

Bonus over the public API: expired cache entries are kept and served when
the upstream is unreachable (stale-while-error), so short API outages
degrade gracefully for everyone instead of failing.

Usage:
    python3 server.py [port]            (default port 8000)

Widget:
    http://<host>:<port>/                (stand-in dashboard, optional)
    http://<host>:<port>/departures.html?api=/api

Deploy: copy this file AND 01_Project/departures.html (and, optionally,
01_Project/index.html) into one folder on the internal host. departures.html
is looked up next to this script first, then in ../01_Project/.

No dependencies beyond the Python standard library.
"""

import os
import sys
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = "https://v6.bvg.transport.rest"
CACHE_TTL = 30  # seconds; matches the API's own cache-control max-age

# path -> (expires_at, body_bytes, content_type)
CACHE = {}

HERE = os.path.dirname(os.path.abspath(__file__))
WIDGET_CANDIDATES = [
    os.path.join(HERE, "departures.html"),
    os.path.join(HERE, "..", "01_Project", "departures.html"),
]
DASHBOARD_CANDIDATES = [
    os.path.join(HERE, "index.html"),
    os.path.join(HERE, "..", "01_Project", "index.html"),
]


def first_existing(paths):
    for p in paths:
        if os.path.isfile(p):
            return p
    return None


class Handler(BaseHTTPRequestHandler):
    server_version = "departure-cache/1.0"

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            self.serve_file(first_existing(DASHBOARD_CANDIDATES))
        elif path == "/departures.html":
            self.serve_file(first_existing(WIDGET_CANDIDATES))
        elif path == "/api" or path.startswith("/api/"):
            self.proxy()
        else:
            self.send_error(404, "Not found")

    def serve_file(self, filepath):
        if not filepath:
            self.send_error(404, "widget file not found next to server.py")
            return
        with open(filepath, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def proxy(self):
        upstream_url = UPSTREAM + self.path[len("/api"):]
        entry = CACHE.get(upstream_url)
        now = time.time()
        if entry and entry[0] > now:
            self.send_json(entry[1], entry[2], "HIT")
            return
        try:
            req = urllib.request.Request(
                upstream_url, headers={"User-Agent": "departure-cache/1.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                body = r.read()
                ctype = r.headers.get("Content-Type", "application/json")
        except (urllib.error.URLError, urllib.error.HTTPError, OSError):
            # Stale-while-error: an expired entry still beats no data.
            if entry:
                self.send_json(entry[1], entry[2], "STALE")
                return
            self.send_error(502, "upstream unreachable: " + upstream_url)
            return
        CACHE[upstream_url] = (now + CACHE_TTL, body, ctype)
        self.send_json(body, ctype, "MISS")

    def send_json(self, body, ctype, cache_status):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("X-Cache-Status", cache_status)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print("departure-board server: http://0.0.0.0:%d/" % port)
    print("widget:                http://<host>:%d/departures.html?api=/api" % port)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
