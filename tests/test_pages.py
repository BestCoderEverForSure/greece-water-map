"""Area-page generation on a small synthetic map: counts, names, slugs, links, escaping, both languages."""
import json
import pathlib
import re

import pytest

from conftest import load

pages = load("build_pages")
BASE = "https://example.test/site/"


def square(x0, y0, x1, y1):
    return {"type": "Polygon", "coordinates": [[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]]}


def area(rel, level, el, en, geom):
    return {"type": "Feature", "geometry": geom,
            "properties": {"level": level, "rel": rel, "iso": "", "name": el, "name_el": el, "name_en": en}}


def point(i, lon, lat, **props):
    p = {"kind": "fountain", "osm": f"n{i}"}
    p.update(props)
    return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": p}


HOSTILE = "Κακό</script><script>alert(1)</script>"


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("site")
    areas = [
        area(1, "unit", "Περιφερειακή Ενότητα Άλφα", "Alfa Regional Unit", square(20, 38, 22, 40)),
        area(2, "municipality", "Δήμος Άλφα", "Alfa Municipality", square(20, 38, 21, 40)),   # same slug as the unit
        area(3, "municipality", HOSTILE, "Evil</script> & <b>Co</b> Municipality", square(21, 38, 22, 40)),
        area(4, "municipality", "Δήμος Άδειος", "Empty Municipality", square(30, 30, 31, 31)),  # too few points
    ]
    water = [point(i, 20.5, 38.5 + i * 0.01, name=f"Βρύση {i}") for i in range(6)]
    water += [point(100 + i, 21.5, 38.5 + i * 0.01, name="<img src=x onerror=alert(1)>", fee="no") for i in range(5)]
    water += [point(200, 30.5, 30.5)]                                   # the empty municipality: 1 point only
    water += [point(300, 50.0, 50.0)]                                   # outside every area
    (out / "water.geojson").write_text(json.dumps({"type": "FeatureCollection", "generated": "2026-01-01", "features": water}))
    (out / "areas.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": areas}))
    pages.main(str(out / "water.geojson"), str(out / "areas.geojson"), str(out), BASE)
    return out


def all_pages(root):
    return sorted(p for p in root.rglob("index.html"))


def test_expected_pages(built):
    rel = sorted(str(p.relative_to(built)) for p in all_pages(built))
    slugs = {p.split("/")[-2] for p in rel if p.count("/") >= 2 and not p.startswith(("vryses/index", "en/areas/index"))}
    assert "alfa" in slugs and "alfa-regional-unit" in slugs            # collision: municipality keeps the plain name
    assert not any("empty" in p for p in rel)                           # fewer than MIN_POINTS -> no thin page
    for lang_dir in ("vryses", "en/areas"):
        assert (built / lang_dir / "index.html").exists()
    assert len(rel) == 2 * 3 + 2                                        # 3 areas x 2 languages + 2 indexes


def test_counts(built):
    el = (built / "vryses/alfa/index.html").read_text(encoding="utf-8")
    assert "6 γνωστά σημεία στον Δήμο Άλφα" in el                       # accusative after "στον"
    en = (built / "en/areas/alfa-regional-unit/index.html").read_text(encoding="utf-8")
    assert "11 known points" in en


def test_hostile_names_never_become_markup(built):
    for p in all_pages(built):
        html = p.read_text(encoding="utf-8")
        body = html.split("<body>", 1)[1]
        assert "<script>alert" not in html
        assert "<img" not in body and "<b>Co" not in body
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            assert "<" not in block
            json.loads(block)                                           # still valid JSON


def test_links_resolve_and_languages_pair_up(built):
    for p in all_pages(built):
        html = p.read_text(encoding="utf-8")
        canon = re.search(r'<link rel="canonical" href="([^"]+)"', html).group(1)
        assert canon.startswith(BASE) and (built / canon[len(BASE):] / "index.html").exists()
        alts = dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', html))
        assert set(alts) == {"el", "en", "x-default"}
        for url in alts.values():
            assert (built / url[len(BASE):] / "index.html").exists()
        assert canon in alts.values()
        for href in re.findall(r'href="([^"]+)"', html):
            href = href.replace("&amp;", "&")
            if href.startswith(BASE) and "#" not in href and "?" not in href:
                assert (built / href[len(BASE):] / "index.html").exists() or href == BASE, href
        assert "Content-Security-Policy" in html and "default-src 'none'" in html


def test_sitemap_and_robots(built):
    sm = (built / "sitemap.xml").read_text(encoding="utf-8")
    locs = re.findall(r"<loc>([^<]+)</loc>", sm)
    assert BASE in locs and len(locs) == len(set(locs))
    for url in locs:
        if url != BASE:
            assert (built / url[len(BASE):] / "index.html").exists(), url
    assert f"Sitemap: {BASE}sitemap.xml" in (built / "robots.txt").read_text()


def test_json_for_script_round_trip():
    value = {"name": "a</script>&<b> "}
    out = pages.json_for_script(value)
    assert "<" not in out and ">" not in out and "&" not in out
    assert json.loads(out) == value


@pytest.mark.parametrize("text, slug", [("Ζαγόρι", "zagori"), ("Άγιος Νικόλαος", "agios-nikolaos"),
                                         ("Κως", "kos"), ("Χανιά", "chania"), ("   ", "area")])
def test_slugify(text, slug):
    assert pages.slugify(text) == slug
