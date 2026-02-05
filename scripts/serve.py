#!/usr/bin/env python3
import argparse
import os
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


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
    os.chdir(root)

    ThreadingHTTPServer.allow_reuse_address = True
    with ThreadingHTTPServer(("", args.port), SimpleHTTPRequestHandler) as httpd:
        if args.open:
            webbrowser.open(f"http://localhost:{args.port}/docs/index.md")
        print(f"Serving {root} at http://localhost:{args.port}")
        print(f"Index: {docs_index}")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
