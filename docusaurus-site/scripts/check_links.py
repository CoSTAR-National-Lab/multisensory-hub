"""Check every link in the built Docusaurus site.

Usage (from the repo root, after `npm run build` in docusaurus-site/):

    uv run python docusaurus-site/scripts/check_links.py [build_dir] [--json out.json] [--no-external]

Checks, for every *.html under the build directory:
  - internal links, images, scripts and stylesheets resolve to a file in the build
  - fragment anchors (#id) exist in the target page's static HTML
  - external http(s) URLs respond (HEAD, falling back to GET); each URL is fetched once

Exit code is 1 if any internal link or anchor is broken. External failures are
reported but do not fail the run: many publishers (DOI landing pages, news sites)
return 403 to scripts while loading fine in a browser, so treat 403 as "verify by hand".
"""
import argparse
import json
import os
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from urllib.parse import unquote, urljoin, urlsplit

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BUILD = os.path.join(HERE, "..", "build")
# Absolute links to the site itself are checked as internal links
SITE_URLS = (
    "https://multisensory.costarnetwork.co.uk",
    "https://costar-national-lab.github.io/multisensory-hub",
)
LINK_ATTRS = (
    ("a", "href"), ("img", "src"), ("link", "href"), ("script", "src"),
    ("iframe", "src"), ("source", "src"), ("video", "src"), ("audio", "src"),
)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/128.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("name"):
            self.ids.add(a["name"])
        for t, k in LINK_ATTRS:
            if tag == t and a.get(k):
                self.links.append((tag, a[k]))
        if tag == "img" and a.get("srcset"):
            for part in a["srcset"].split(","):
                url = part.strip().split(" ")[0]
                if url:
                    self.links.append(("img", url))


def load_pages(build: str) -> dict[str, PageParser]:
    pages = {}
    for root, _, files in os.walk(build):
        for f in files:
            if f.endswith(".html"):
                full = os.path.join(root, f)
                rel = "/" + os.path.relpath(full, build).replace(os.sep, "/")
                p = PageParser()
                with open(full, encoding="utf-8") as fh:
                    p.feed(fh.read())
                pages[rel] = p
    return pages


def resolve_local(build: str, path: str) -> str | None:
    """Map a URL path to a file in the build (Docusaurus emits both x.html and x/index.html)."""
    path = unquote(path)
    if path.endswith("/"):
        cands = [path + "index.html", path[:-1] + ".html"]
    else:
        cands = [path, path + ".html", path + "/index.html"]
    for c in cands:
        if os.path.isfile(os.path.join(build, c.lstrip("/"))):
            return "/" + c.lstrip("/")
    return None


def check_external(url: str):
    try:
        r = requests.head(url, headers=HEADERS, timeout=20, allow_redirects=True)
        if r.status_code >= 400:
            r = requests.get(url, headers=HEADERS, timeout=25, allow_redirects=True, stream=True)
        return url, r.status_code, r.url if r.url != url else "", ""
    except Exception as e:  # noqa: BLE001
        return url, None, "", f"{type(e).__name__}: {str(e)[:120]}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("build", nargs="?", default=DEFAULT_BUILD)
    ap.add_argument("--json", help="write full results to this file")
    ap.add_argument("--no-external", action="store_true", help="skip HTTP checks")
    args = ap.parse_args()
    build = os.path.abspath(args.build)
    if not os.path.isdir(build):
        print(f"build dir not found: {build}", file=sys.stderr)
        return 2

    pages = load_pages(build)
    internal_broken, anchor_broken = [], []
    external: dict[str, set[str]] = defaultdict(set)

    for page, p in pages.items():
        for tag, href in p.links:
            h = href.strip()
            if not h or h.startswith(("javascript:", "mailto:", "tel:", "data:")):
                continue
            for s in SITE_URLS:
                if h.startswith(s):
                    h = h[len(s):] or "/"
            sp = urlsplit(h)
            if sp.scheme in ("http", "https"):
                external[h].add(page)
                continue
            if sp.scheme:
                continue
            target = urlsplit(urljoin("https://x" + page, h))
            if h.startswith("#"):
                tfile = page
            else:
                tfile = resolve_local(build, target.path or page)
                if not tfile:
                    internal_broken.append((page, tag, href))
                    continue
            if target.fragment and tfile in pages and unquote(target.fragment) not in pages[tfile].ids:
                anchor_broken.append((page, href))

    results = []
    if not args.no_external:
        with ThreadPoolExecutor(16) as ex:
            results = list(ex.map(check_external, sorted(external)))

    print(f"pages: {len(pages)}   external urls: {len(external)}")
    print(f"broken internal links: {len(internal_broken)}")
    for page, tag, href in internal_broken:
        print(f"  {page}  <{tag}>  {href}")
    print(f"broken anchors: {len(anchor_broken)}")
    for page, href in anchor_broken:
        print(f"  {page}  {href}")
    if results:
        bad = [r for r in results if r[1] is None or r[1] >= 400]
        print(f"external failures: {len(bad)}  (403 usually means bot-blocking – check in a browser)")
        for url, status, _, err in sorted(bad, key=lambda r: (str(r[1]), r[0])):
            print(f"  {status}  {url}  {err}".rstrip())
        moved = [r for r in results if r[2] and r[1] and r[1] < 400]
        print(f"redirected: {len(moved)}")
        for url, status, final, _ in moved:
            print(f"  {status}  {url}\n        -> {final}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({
                "pages": len(pages),
                "internal_broken": internal_broken,
                "anchor_broken": anchor_broken,
                "external": [
                    {"url": u, "status": s, "final": f, "error": e, "pages": sorted(external[u])}
                    for u, s, f, e in results
                ],
            }, fh, indent=1)
    return 1 if internal_broken or anchor_broken else 0


if __name__ == "__main__":
    sys.exit(main())
