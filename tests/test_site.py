"""Checks on the real site folder: files the app and service worker need exist, stamps are current,
generated pages link correctly, and the data file is sane. Run before every publish and in the weekly job."""
import json
import re

import pytest

from conftest import AREAS, load

GREECE = (19.0, 34.5, 30.0, 42.0)   # lon/lat box with a margin


def test_asset_stamps_current(site):
    load("stamp_assets").main(str(site), check=True)


def test_app_references_exist(site):
    html = (site / "index.html").read_text(encoding="utf-8")
    for ref in re.findall(r'(?:src|href)="([^"#:]+)"', html):
        path = ref.split("?")[0]
        if path.endswith("/"):
            continue                                                    # area index links, checked below
        assert (site / path).exists(), ref
    assert "Content-Security-Policy" in html and "'unsafe-inline'" not in html.split("Content-Security-Policy")[1].split(">")[0]
    assert "<script>" not in html                                       # no inline script (CSP)


def test_service_worker_precache_exists(site):
    sw = (site / "sw.js").read_text(encoding="utf-8")
    lib = re.search(r'const LIB = "([^"]+)"', sw).group(1)
    listed = re.search(r"const PRECACHE = \[(.*?)\];", sw, re.S).group(1).replace("LIB + ", "")
    for item in re.findall(r'"([^"]+)"', listed):
        path = (lib + item if not item.startswith("./") else item)[2:]
        assert path == "" or (site / path).exists(), item
    assert re.search(r'const VERSION = "v\d+"', sw)


def test_manifest_icons_exist(site):
    manifest = json.loads((site / "manifest.webmanifest").read_text(encoding="utf-8"))
    for icon in manifest["icons"]:
        assert (site / icon["src"]).exists(), icon["src"]


def test_water_data_sane(site):
    data = json.loads((site / "water.geojson").read_text(encoding="utf-8"))
    feats = data["features"]
    assert 3000 < len(feats) < 20000
    seen = set()
    for f in feats:
        p, (lon, lat) = f["properties"], f["geometry"]["coordinates"]
        assert GREECE[0] <= lon <= GREECE[2] and GREECE[1] <= lat <= GREECE[3], p["osm"]
        assert p["kind"] in {"fountain", "tap", "spring", "point"}
        assert p.get("drinking_water") != "no" and p.get("access") not in ("private", "no")
        assert re.fullmatch(r"[nw]\d+", p["osm"]) and p["osm"] not in seen
        seen.add(p["osm"])


def test_water_data_inside_greece(site):
    if not AREAS.exists():
        pytest.skip("no areas file")
    from shapely.geometry import Point, shape
    from shapely.prepared import prep
    country = [a for a in json.loads(AREAS.read_text(encoding="utf-8"))["features"] if a["properties"]["level"] == "country"]
    assert len(country) == 1
    inside = prep(shape(country[0]["geometry"]))
    outside = [f["properties"]["osm"] for f in json.loads((site / "water.geojson").read_text(encoding="utf-8"))["features"]
               if not inside.contains(Point(*f["geometry"]["coordinates"]))]
    assert not outside, f"{len(outside)} points outside Greece, e.g. {outside[:5]}"


def generated(site):
    return sorted(list((site / "vryses").rglob("index.html")) + list((site / "en").rglob("index.html")))


def test_generated_pages_link_correctly(site):
    files = generated(site)
    if not files:
        pytest.skip("area pages not generated in this folder")
    sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
    base = re.search(r"<loc>([^<]+)</loc>", sitemap).group(1)
    for url in re.findall(r"<loc>([^<]+)</loc>", sitemap):
        rel = url[len(base):]
        assert rel == "" or (site / rel / "index.html").exists(), url
    for p in files:
        html = p.read_text(encoding="utf-8")
        for href in re.findall(r'href="([^"]+)"', html):
            href = href.replace("&amp;", "&")
            if href.startswith(base) and "#" not in href and "?" not in href and href != base:
                assert (site / href[len(base):] / "index.html").exists(), f"{p}: {href}"
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            assert "<" not in block
            json.loads(block)
