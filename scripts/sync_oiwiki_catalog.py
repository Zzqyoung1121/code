#!/usr/bin/env python3
"""Fetch OI-wiki sitemap and generate ui/catalog.json metadata.
Stores only titles/URLs, not article content.
"""
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

SITEMAP_URL = "https://oi-wiki.org/sitemap.xml"
ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "ui" / "catalog.json"


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


def build_catalog(xml_bytes: bytes):
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
            section = "home"
            title = "index"
            oid = "home/index"
        else:
            parts = path.split("/")
            section = parts[0]
            title = slug_to_title(parts[-1])
            oid = oid_from_path(path)
        by_section[section].append({"oid": oid, "title": title, "url": url})

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


def main() -> None:
    try:
        with urllib.request.urlopen(SITEMAP_URL, timeout=30) as resp:
            data = resp.read()
        catalog = build_catalog(data)
        OUT_FILE.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {OUT_FILE} with {len(catalog)} sections.")
    except Exception as exc:
        print(f"[WARN] Failed to fetch {SITEMAP_URL}: {exc}")
        print(f"[WARN] Keep existing catalog file: {OUT_FILE}")


if __name__ == "__main__":
    main()
