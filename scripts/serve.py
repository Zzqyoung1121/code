#!/usr/bin/env python3
import argparse
import os
import socket
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class UTF8RequestHandler(SimpleHTTPRequestHandler):
    """Force UTF-8 charset for text-like responses to avoid mojibake on Windows."""

    def guess_type(self, path: str) -> str:
        ctype = super().guess_type(path)
        lower = path.lower()

        if lower.endswith(".md"):
            return "text/markdown; charset=utf-8"

        if ctype.startswith("text/") and "charset=" not in ctype:
            return f"{ctype}; charset=utf-8"

        if ctype in {"application/javascript", "application/json", "application/xml"}:
            return f"{ctype}; charset=utf-8"

        return ctype


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve the NOI template library locally.")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the index page in the default browser",
    )
    return parser.parse_args()


def get_lan_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    docs_index = root / "ui" / "index.html"
    os.chdir(root)

    ThreadingHTTPServer.allow_reuse_address = True
    with ThreadingHTTPServer((args.host, args.port), UTF8RequestHandler) as httpd:
        if args.open:
            webbrowser.open(f"http://localhost:{args.port}/ui/index.html")

        lan_ip = get_lan_ip()
        print(f"Serving {root}")
        print(f"Local: http://localhost:{args.port}/ui/index.html")
        print(f"LAN:   http://{lan_ip}:{args.port}/ui/index.html")
        print(f"Index: {docs_index}")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
