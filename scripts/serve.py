#!/usr/bin/env python3
import argparse
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from pathlib import Path
import webbrowser


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve the NOI template library locally.")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the index page in the default browser",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    docs_index = root / "docs" / "index.md"

    handler = SimpleHTTPRequestHandler
    with TCPServer(("", args.port), handler) as httpd:
        if args.open:
            webbrowser.open(f"http://localhost:{args.port}/docs/index.md")
        print(f"Serving {root} at http://localhost:{args.port}")
        print(f"Open {docs_index} for the index.")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
