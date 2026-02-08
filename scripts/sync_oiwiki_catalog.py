#!/usr/bin/env python3
"""Generate ui/catalog.json from OI-Wiki metadata only.

Priority:
1) https://oi-wiki.org/sitemap.xml
2) GitHub API tree of OI-wiki/OI-wiki (docs/**/*.md)

Only title/url/oid metadata is stored.
"""
import argparse
import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

SITEMAP_URL = "https://oi-wiki.org/sitemap.xml"
GITHUB_TREE_URL = "https://api.github.com/repos/OI-wiki/OI-wiki/git/trees/master?recursive=1"
ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "ui" / "catalog.json"
DEFAULT_LOCAL_CANDIDATES = [
    ROOT / "OI-wiki",
    ROOT.parent / "OI-wiki",
]


def slug_to_title(slug: str) -> str:
    slug = slug.strip("/")
    if not slug:
        return "index"
    slug = slug.replace("-", " ")
    slug = re.sub(r"\s+", " ", slug)
    return slug


def oid_from_path(path: str) -> str:
    parts = [p for p in path.strip("/").split("/") if p]
    if not parts:
        return "home/index"
    if len(parts) == 1:
        return f"{parts[0]}/index"
    return f"{parts[0]}/{parts[-1]}"


def dedupe_and_sort(by_section: dict[str, list[dict[str, str]]]):
    catalog = []
    for section in sorted(by_section.keys()):
        seen = set()
        items = []
        for it in sorted(by_section[section], key=lambda x: (x["title"], x["url"])):
            key = (it["oid"], it["url"])
            if key in seen:
                continue
            seen.add(key)
            items.append(it)
        catalog.append({"section": section, "items": items})
    return catalog


def build_catalog_from_sitemap(xml_bytes: bytes):
    root = ET.fromstring(xml_bytes)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    by_section: dict[str, list[dict[str, str]]] = defaultdict(list)

    for loc in root.findall("sm:url/sm:loc", ns):
        url = (loc.text or "").strip()
        if not url.startswith("https://oi-wiki.org/"):
            continue
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        if not path:
            section, title, oid = "home", "index", "home/index"
        else:
            parts = path.split("/")
            section = parts[0]
            title = slug_to_title(parts[-1])
            oid = oid_from_path(path)
        by_section[section].append({"oid": oid, "title": title, "url": url})

    return dedupe_and_sort(by_section)


def build_catalog_from_github_tree(tree_json: dict):
    by_section: dict[str, list[dict[str, str]]] = defaultdict(list)

    for node in tree_json.get("tree", []):
        if node.get("type") != "blob":
            continue
        path = node.get("path", "")
        if not path.startswith("docs/") or not path.endswith(".md"):
            continue

        rel = path[len("docs/") : -len(".md")]
        if rel.endswith("README"):
            rel = rel[:-len("README")].rstrip("/")
        if not rel:
            section = "home"
            page = "index"
        else:
            parts = [p for p in rel.split("/") if p]
            section = parts[0]
            page = parts[-1]

        oid = oid_from_path(rel)
        title = slug_to_title(page)
        oi_url = "https://oi-wiki.org/" + rel.strip("/") + "/"
        by_section[section].append({"oid": oid, "title": title, "url": oi_url})

    return dedupe_and_sort(by_section)


def write_catalog(catalog):
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(len(sec["items"]) for sec in catalog)
    print(f"Wrote {OUT_FILE} with {len(catalog)} sections / {total} entries.")


def fetch(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "codex-catalog-sync/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def build_catalog_from_local_docs(repo_root: Path):
    docs_root = repo_root / "docs"
    if not docs_root.exists():
        raise FileNotFoundError(f"Missing docs directory: {docs_root}")

    by_section: dict[str, list[dict[str, str]]] = defaultdict(list)

    for md_file in docs_root.rglob("*.md"):
        rel_path = md_file.relative_to(docs_root).as_posix()
        if rel_path.endswith("README.md"):
            rel_path = rel_path[: -len("README.md")].rstrip("/")
        if not rel_path:
            section = "home"
            page = "index"
        else:
            parts = [p for p in rel_path.split("/") if p]
            section = parts[0]
            page = parts[-1]

        oid = oid_from_path(rel_path)
        title = slug_to_title(page)
        oi_url = "https://oi-wiki.org/" + rel_path.strip("/") + "/"
        by_section[section].append({"oid": oid, "title": title, "url": oi_url})

    return dedupe_and_sort(by_section)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync OI-Wiki catalog metadata.")
    parser.add_argument(
        "--local",
        type=Path,
        default=None,
        help="Path to a local OI-wiki repo (uses docs/).",
    )
    return parser.parse_args()


def resolve_local_repo(local_arg: Path | None) -> Path | None:
    if local_arg:
        return local_arg
    env_path = Path(os.environ.get("OI_WIKI_DIR", "")).expanduser()
    if env_path.exists():
        return env_path
    for candidate in DEFAULT_LOCAL_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def main() -> None:
    args = parse_args()
    local_repo = resolve_local_repo(args.local)
    if local_repo:
        try:
            catalog = build_catalog_from_local_docs(local_repo)
            write_catalog(catalog)
            return
        except Exception as exc:
            print(f"[WARN] Failed local repo scan ({local_repo}): {exc}")

    try:
        catalog = build_catalog_from_sitemap(fetch(SITEMAP_URL))
        write_catalog(catalog)
        return
    except Exception as exc:
        print(f"[WARN] Failed sitemap fetch: {exc}")

    try:
        tree = json.loads(fetch(GITHUB_TREE_URL).decode("utf-8"))
        catalog = build_catalog_from_github_tree(tree)
        write_catalog(catalog)
        return
    except Exception as exc:
        print(f"[WARN] Failed github tree fetch: {exc}")

    print(f"[WARN] Keep existing catalog file: {OUT_FILE}")


if __name__ == "__main__":
    main()
