"""Filter drinking-water points out of a Geofabrik OSM extract into GeoJSON.

Usage: .venv/bin/python extract.py data/greece.osm.pbf data/water.geojson
Data © OpenStreetMap contributors (ODbL).
"""
import datetime
import json
import sys

import osmium

KEEP_TAGS = ("name", "name:el", "name:en", "drinking_water", "bottle", "fee",
             "access", "seasonal", "opening_hours", "operator", "check_date",
             "description", "wheelchair", "dog", "bench", "covered")


def classify(tags):
    """Return a coarse kind for a feature, or None if it isn't drinking water."""
    if tags.get("drinking_water") == "no" or tags.get("access") == "private":
        return None
    if tags.get("amenity") == "drinking_water":
        return "fountain"
    if tags.get("man_made") == "water_tap":
        return "tap"
    if tags.get("natural") == "spring":
        return "spring"
    if tags.get("amenity") == "fountain" and tags.get("drinking_water") == "yes":
        return "fountain"
    if tags.get("drinking_water") == "yes":       # camp sites, wells, water points, toilets, ...
        return "point"
    return None


def main(src, dst):
    feats = []
    fp = (osmium.FileProcessor(src, osmium.osm.NODE | osmium.osm.WAY)
          .with_locations()
          .with_filter(osmium.filter.KeyFilter("amenity", "man_made", "natural", "tourism", "drinking_water")))
    for o in fp:
        kind = classify(o.tags)
        if not kind:
            continue
        if o.is_node():
            if not o.location.valid():
                continue
            lon, lat = o.location.lon, o.location.lat
        else:
            pts = [(n.lon, n.lat) for n in o.nodes if n.location.valid()]
            if not pts:
                continue
            lon = sum(p[0] for p in pts) / len(pts)
            lat = sum(p[1] for p in pts) / len(pts)
        props = {k: o.tags[k] for k in KEEP_TAGS if k in o.tags}
        props["kind"] = kind
        props["osm"] = ("n" if o.is_node() else "w") + str(o.id)
        feats.append({"type": "Feature",
                      "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
                      "properties": props})
    with open(dst, "w") as f:
        json.dump({"type": "FeatureCollection", "generated": datetime.date.today().isoformat(), "features": feats}, f, ensure_ascii=False)
    by = {}
    for ft in feats:
        by[ft["properties"]["kind"]] = by.get(ft["properties"]["kind"], 0) + 1
    print(len(feats), "features", by)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
