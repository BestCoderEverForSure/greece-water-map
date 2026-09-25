"""What counts as a water point, and an end-to-end run of the extractor on a tiny OSM file."""
import json

import pytest

from conftest import load

extract = load("extract")


@pytest.mark.parametrize("tags, kind", [
    ({"amenity": "drinking_water"}, "fountain"),
    ({"amenity": "drinking_water", "drinking_water": "yes"}, "fountain"),
    ({"man_made": "water_tap"}, "tap"),
    ({"natural": "spring"}, "spring"),
    ({"natural": "spring", "drinking_water": "yes"}, "spring"),
    ({"amenity": "fountain", "drinking_water": "yes"}, "fountain"),
    ({"tourism": "camp_site", "drinking_water": "yes"}, "point"),
    ({"man_made": "water_well", "drinking_water": "yes"}, "point"),
    # excluded
    ({"amenity": "fountain"}, None),                                   # decorative fountain
    ({"amenity": "drinking_water", "drinking_water": "no"}, None),
    ({"man_made": "water_tap", "drinking_water": "no"}, None),
    ({"natural": "spring", "drinking_water": "no"}, None),
    ({"amenity": "drinking_water", "access": "private"}, None),
    ({"amenity": "drinking_water", "access": "no"}, None),
    ({"amenity": "toilets"}, None),
    ({"tourism": "camp_site"}, None),
    ({}, None),
])
def test_classify(tags, kind):
    assert extract.classify(tags) == kind


OSM = """<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="test">
  <node id="1" lat="37.9755" lon="23.7348" version="1"><tag k="amenity" v="drinking_water"/><tag k="name" v="Βρύση &lt;b&gt;"/><tag k="bottle" v="yes"/></node>
  <node id="2" lat="37.9760" lon="23.7350" version="1"><tag k="amenity" v="drinking_water"/><tag k="drinking_water" v="no"/></node>
  <node id="3" lat="39.10" lon="21.00" version="1"><tag k="natural" v="spring"/></node>
  <node id="4" lat="37.9800" lon="23.7400" version="1"><tag k="amenity" v="fountain"/></node>
  <node id="5" lat="37.9900" lon="23.7500" version="1"><tag k="secret" v="x"/></node>
  <node id="10" lat="38.0000" lon="23.8000" version="1"/>
  <node id="11" lat="38.0000" lon="23.8010" version="1"/>
  <node id="12" lat="38.0010" lon="23.8010" version="1"/>
  <way id="20" version="1"><nd ref="10"/><nd ref="11"/><nd ref="12"/><nd ref="10"/><tag k="man_made" v="water_tap"/></way>
</osm>
"""


def test_extract_end_to_end(tmp_path):
    src, dst = tmp_path / "t.osm", tmp_path / "w.geojson"
    src.write_text(OSM, encoding="utf-8")
    extract.main(str(src), str(dst))
    data = json.loads(dst.read_text(encoding="utf-8"))
    by_id = {f["properties"]["osm"]: f for f in data["features"]}
    assert set(by_id) == {"n1", "n3", "w20"}
    assert by_id["n1"]["properties"]["kind"] == "fountain"
    assert by_id["n1"]["properties"]["name"] == "Βρύση <b>"            # kept as text; the app never renders it as HTML
    assert by_id["n1"]["properties"]["bottle"] == "yes"
    assert "secret" not in json.dumps(data)                           # only whitelisted tags are copied
    lon, lat = by_id["w20"]["geometry"]["coordinates"]
    assert 23.80 <= lon <= 23.802 and 38.0 <= lat <= 38.001           # way reduced to a point inside it
    assert data["generated"]
