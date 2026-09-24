from __future__ import annotations

import argparse
import mimetypes
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "site"
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("image/avif", ".avif")
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("image/svg+xml", ".svg")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self) -> None:
        clean = self.path.split("?", 1)[0]
        requested = ROOT / clean.lstrip("/")
        if clean != "/" and not requested.exists():
            self.path = "/index.html"
        super().do_GET()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serve the local PULL.FUN homepage mirror")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=4177, type=int)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Serving {ROOT} at http://{args.host}:{args.port}", flush=True)
    server.serve_forever()
