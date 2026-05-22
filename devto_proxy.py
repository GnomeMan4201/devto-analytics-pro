#!/usr/bin/env python3
"""
devto_proxy.py — local proxy for dev.to analytics
Adds the api-key header server-side, bypassing browser CORS restrictions.
Usage: DEVTO_API_KEY=your_key python3 devto_proxy.py
Then open http://localhost:8765/devto_analytics.html
"""
import sys
import json
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

import os
API_KEY = os.environ.get("DEVTO_API_KEY", "")
SERVE_DIR = Path(__file__).parent
PORT = 8765

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} {fmt % args}")

    def do_GET(self):
        if self.path == '/':
            self.path = '/devto_analytics.html'
        # Proxy /api/* to dev.to with the api-key header
        if self.path.startswith("/api/"):
            devto_url = "https://dev.to" + self.path
            req = urllib.request.Request(devto_url, headers={
                "api-key": API_KEY,
                "Accept": "application/json",
                "User-Agent": "devto-analytics-proxy/1.0",
            })
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    body = resp.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(body)
            except urllib.error.HTTPError as e:
                body = e.read()
                self.send_response(e.code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self.send_response(502)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        # Serve static files from the same directory
        file_path = SERVE_DIR / self.path.lstrip("/")
        if self.path == "/" or not file_path.exists():
            file_path = SERVE_DIR / "devto_analytics.html"
        if file_path.exists() and file_path.is_file():
            suffix = file_path.suffix.lower()
            ctype = {"html": "text/html", "js": "text/javascript", "css": "text/css"}.get(suffix[1:], "text/plain")
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.end_headers()
            self.wfile.write(file_path.read_bytes())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

if __name__ == "__main__":
    if not API_KEY:
        print("usage: python3 devto_proxy.py YOUR_DEV_TO_API_KEY")
        sys.exit(1)
    print(f"proxy running → http://localhost:{PORT}/devto_analytics.html")
    print(f"api key: {API_KEY[:6]}{'*' * (len(API_KEY)-6)}")
    HTTPServer(("", PORT), Handler).serve_forever()
