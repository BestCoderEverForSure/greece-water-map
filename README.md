# Νεράκι (Neraki): Greece drinking-water map

A free map of drinking fountains, taps and springs in Greece (prototype).

- Data: © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), available under the [ODbL](https://opendatacommons.org/licenses/odbl/). `water.geojson` is a filtered extract of OSM (amenity=drinking_water, man_made=water_tap, natural=spring, and drinkable amenity=fountain).
- Map tiles: [OpenFreeMap](https://openfreemap.org), © OpenMapTiles, data from OpenStreetMap.
- Water is not guaranteed safe to drink. Information comes from OSM users and is not verified.
- Missing or wrong? Use the "Missing a fountain?" button on the map (creates an OpenStreetMap note) or edit OpenStreetMap directly.

## Data refresh
A GitHub Action (`.github/workflows/refresh-data.yml`) runs every Monday: it downloads the Greece extract from [Geofabrik](https://download.geofabrik.de/europe/greece.html), rebuilds `water.geojson` with `tools/extract.py`, and commits only if the data changed. You can also run it by hand from the Actions tab.

## Area pages
`tools/build_pages.py` writes a static Greek page for every regional unit and municipality with at least 5 known points (Greek: `vryses/<area>/`, English: `en/areas/<area>/`), an index page, `sitemap.xml` and `robots.txt`. Boundaries come from OpenStreetMap (`tools/areas.geojson`, built once with `tools/build_areas.py`). The weekly job rebuilds the pages. When the site gets its own domain, change `SITE_URL` in the workflow (and the canonical/og:url tags in `index.html`), and re-run the job.

## Tests
`python -m pytest -q tests` checks the extractor's rules, page generation (links, both languages, escaping of hostile names), that `index.html` references current asset versions, that everything the service worker precaches exists, and that the data file is sane. The weekly job runs them before publishing, and refuses to publish if the download's checksum is wrong or more than 15% of the points vanish in a week.

## Changing the app
After editing `app.js` or `app.css`, run `python tools/stamp_assets.py .` so browsers fetch the new versions. The map library is self-hosted in `vendor/maplibre-gl-4.7.1/` (BSD-3-Clause, checksum-verified against npm).
