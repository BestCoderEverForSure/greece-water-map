"""Extract Greek regional-unit (admin_level 5) and municipality (admin_level 6) boundaries from an OSM extract.

Usage: .venv/bin/python build_areas.py data/greece.osm.pbf web/areas.geojson
Output: a GeoJSON file of simplified polygons with names. Run rarely: boundaries change slowly.
Data © OpenStreetMap contributors (ODbL).
"""
import json
import sys

import osmium
import shapely
from shapely.geometry import mapping
from shapely.ops import unary_union

LEVELS = {"6": "unit", "7": "municipality"}   # Greece: 5 = region, 6 = regional unit, 7 = municipality
# Greece's national boundary (it includes territorial waters) is kept too, as level "country". It is only used to
# drop points from neighbouring countries that the download's buffer includes; the app never draws it.


def main(src, dst):
    wkb = osmium.geom.WKBFactory()
    feats, raw, country = [], [], None
    fp = (osmium.FileProcessor(src, osmium.osm.RELATION | osmium.osm.NODE | osmium.osm.WAY)
          .with_areas(osmium.filter.TagFilter(("boundary", "administrative"))))
    for o in fp:
        if not o.is_area() or o.from_way():
            continue
        t = o.tags
        lvl = t.get("admin_level")
        if lvl == "2" and t.get("ISO3166-1") == "GR":
            geom = shapely.from_wkb(bytes.fromhex(wkb.create_multipolygon(o))).simplify(0.0005, preserve_topology=True)
            country = {"type": "Feature", "geometry": mapping(geom),
                       "properties": {"level": "country", "rel": o.orig_id(), "iso": "GR", "name": t.get("name", ""),
                                      "name_el": t.get("name:el", ""), "name_en": t.get("name:en", "")}}
            continue
        if t.get("boundary") != "administrative" or lvl not in LEVELS:
            continue
        try:
            geom = shapely.from_wkb(bytes.fromhex(wkb.create_multipolygon(o)))
        except Exception as e:  # broken multipolygon: skip it
            print("skip", o.orig_id(), e, file=sys.stderr)
            continue
        geom = geom.simplify(0.0006, preserve_topology=True)
        if geom.is_empty:
            continue
        raw.append((LEVELS[lvl], geom, {
            "level": LEVELS[lvl], "rel": o.orig_id(), "iso": t.get("ISO3166-2", ""),
            "name": t.get("name", ""), "name_el": t.get("name:el", t.get("name", "")),
            "name_en": t.get("name:en", ""),
        }))
    # Keep only Greek areas: regional units carry an ISO3166-2 "GR-.." code; a municipality must sit inside one.
    is_gr_unit = lambda pr: ("Περιφερειακή Ενότητα" in pr["name"] or "Regional Unit" in pr["name_en"] or "Regional Unit" in pr["name"]
                             or "Regional unit" in pr["name_en"] or pr["iso"].startswith("GR"))
    greece = unary_union([g for lv, g, pr in raw if lv == "unit" and is_gr_unit(pr)])
    for lv, geom, pr in raw:
        ok = is_gr_unit(pr) if lv == "unit" else greece.contains(geom.representative_point())
        if ok:
            feats.append({"type": "Feature", "geometry": mapping(geom), "properties": pr})
    feats.sort(key=lambda f: (f["properties"]["level"], f["properties"]["name_el"]))
    if country is None:
        raise SystemExit("Greece's national boundary was not found in the extract")
    feats.insert(0, country)
    with open(dst, "w") as f:
        json.dump({"type": "FeatureCollection", "features": feats}, f, ensure_ascii=False, separators=(",", ":"))
    by = {}
    for ft in feats:
        by[ft["properties"]["level"]] = by.get(ft["properties"]["level"], 0) + 1
    print(len(feats), "areas", by)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
