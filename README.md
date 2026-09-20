# Νεράκι (Neraki): Greece drinking-water map

A free map of drinking fountains, taps and springs in Greece (prototype).

- Data: © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), available under the [ODbL](https://opendatacommons.org/licenses/odbl/). `water.geojson` is a filtered extract of OSM (amenity=drinking_water, man_made=water_tap, natural=spring, and drinkable amenity=fountain).
- Map tiles: [OpenFreeMap](https://openfreemap.org), © OpenMapTiles, data from OpenStreetMap.
- Water is not guaranteed safe to drink. Information comes from OSM users and is not verified.
- Missing or wrong? Use the "Missing a fountain?" button on the map (creates an OpenStreetMap note) or edit OpenStreetMap directly.

## Data refresh
A GitHub Action (`.github/workflows/refresh-data.yml`) runs every Monday: it downloads the Greece extract from [Geofabrik](https://download.geofabrik.de/europe/greece.html), rebuilds `water.geojson` with `tools/extract.py`, and commits only if the data changed. You can also run it by hand from the Actions tab.
