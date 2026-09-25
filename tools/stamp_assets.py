"""Stamp app.js and app.css in index.html with a short content hash (?v=...), so a new page never runs old code.

Usage: python stamp_assets.py SITE_DIR          (rewrites SITE_DIR/index.html in place)
       python stamp_assets.py SITE_DIR --check  (exit 1 if the stamps are out of date; used by the tests)
Run it after every change to app.js or app.css, before publishing.
"""
import hashlib
import os
import re
import sys

ASSETS = ("app.js", "app.css")


def digest(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:10]


def stamped(html, site):
    for name in ASSETS:
        v = digest(os.path.join(site, name))
        html, n = re.subn(rf'(["\']){re.escape(name)}(\?v=[0-9a-f]*)?\1', rf"\1{name}?v={v}\1", html)
        if n != 1:
            raise SystemExit(f"expected exactly one reference to {name} in index.html, found {n}")
    return html


def main(site, check=False):
    path = os.path.join(site, "index.html")
    html = open(path, encoding="utf-8").read()
    new = stamped(html, site)
    if check:
        if new != html:
            raise SystemExit("index.html asset stamps are out of date: run stamp_assets.py")
        print("asset stamps up to date")
        return
    if new != html:
        open(path, "w", encoding="utf-8").write(new)
    print("stamped:", ", ".join(f"{n}?v={digest(os.path.join(site, n))}" for n in ASSETS))


if __name__ == "__main__":
    main(sys.argv[1], "--check" in sys.argv[2:])
