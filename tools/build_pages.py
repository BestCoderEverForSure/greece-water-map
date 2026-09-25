"""Generate static, search-engine-friendly pages in Greek and English: one per Greek regional unit and municipality.

Usage: python build_pages.py water.geojson areas.geojson OUT_DIR [BASE_URL]
Greek:   OUT_DIR/vryses/<slug>/index.html      and OUT_DIR/vryses/index.html
English: OUT_DIR/en/areas/<slug>/index.html    and OUT_DIR/en/areas/index.html
Also OUT_DIR/sitemap.xml and OUT_DIR/robots.txt.
Data © OpenStreetMap contributors (ODbL).
"""
import html
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict

from shapely.geometry import Point, shape
from shapely.strtree import STRtree

MIN_POINTS = 5          # areas with fewer known points get no page (avoids thin pages)
MAX_LISTED = 120        # points listed on a page
GREEK = {"α": "a", "β": "v", "γ": "g", "δ": "d", "ε": "e", "ζ": "z", "η": "i", "θ": "th", "ι": "i", "κ": "k", "λ": "l",
         "μ": "m", "ν": "n", "ξ": "x", "ο": "o", "π": "p", "ρ": "r", "σ": "s", "ς": "s", "τ": "t", "υ": "y", "φ": "f",
         "χ": "ch", "ψ": "ps", "ω": "o"}
DIRS = {"el": "vryses", "en": "en/areas"}

TXT = {
    "el": {
        "lang": "el", "switch": "English", "areas": "Περιοχές", "brand": "Νεράκι",
        "kinds": {"fountain": "Βρύση", "tap": "Κάνουλα", "spring": "Πηγή", "point": "Σημείο νερού"},
        "free": "Δωρεάν", "bottle": "Γέμισμα μπουκαλιού", "fallback_point": "Σημείο",
        "footer": "Τα δεδομένα είναι από το OpenStreetMap, έναν ανοιχτό χάρτη που φτιάχνουν εθελοντές (© OpenStreetMap contributors, ODbL). Το νερό δεν είναι εγγυημένα ασφαλές: οι πληροφορίες προέρχονται από εθελοντές και δεν έχουν ελεγχθεί από εμάς. Αν δεν είσαι σίγουρος, ρώτα ή πάρε δικό σου νερό.",
        "open_map": "Άνοιγμα στον χάρτη", "open_map_full": "Άνοιγμα του χάρτη",
        "s_total": "σημεία συνολικά", "s_drink": "πόσιμο νερό", "s_other": "πηγές και κάνουλες (μη επιβεβαιωμένες)",
        "h_munis": "Δήμοι", "h_neigh": "Γειτονικοί δήμοι στην ίδια ενότητα", "h_missing": "Λείπει κάποια βρύση;",
    },
    "en": {
        "lang": "en", "switch": "Ελληνικά", "areas": "Areas", "brand": "Νεράκι",
        "kinds": {"fountain": "Fountain", "tap": "Tap", "spring": "Spring", "point": "Water point"},
        "free": "Free", "bottle": "Bottle refill", "fallback_point": "Point",
        "footer": "Data is from OpenStreetMap, an open map made by volunteers (© OpenStreetMap contributors, ODbL). Water isn't guaranteed safe: the information comes from volunteers and isn't checked by us. If you're unsure, ask locally or carry your own water.",
        "open_map": "Open on the map", "open_map_full": "Open the map",
        "s_total": "points in total", "s_drink": "drinking water", "s_other": "springs and taps (unconfirmed)",
        "h_munis": "Municipalities", "h_neigh": "Neighbouring municipalities in the same unit", "h_missing": "Missing a fountain?",
    },
}


def translit(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("ου", "ou").replace("γγ", "ng").replace("γκ", "gk")
    return "".join(GREEK.get(c, c) for c in s)


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", translit(s)).strip("-")
    return s or "area"


def names(pr):
    """(Greek display name, English display name, slug)."""
    el = pr["name_el"] or pr["name"]
    en = pr["name_en"]
    bare_el = re.sub(r"^(Δήμος|Περιφερειακή Ενότητα|Μητροπολιτική Ενότητα)\s+", "", el)
    base_en = re.sub(r"\b(Municipality of|Regional Unit|Regional unit|Metropolitan Unit|Municipality)\b", "", en).strip() if en else ""
    slug = slugify(base_en or bare_el)
    if not en:
        words = translit(bare_el).replace("-", " ").title()
        en = f"{words} Regional Unit" if pr["level"] == "unit" else f"Municipality of {words}"
    return el, en, slug


def esc(x):
    return html.escape(str(x), quote=True)


def json_for_script(obj):
    """JSON that is safe inside a <script> element: names come from volunteer-edited map data."""
    return (json.dumps(obj, ensure_ascii=False)
            .replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def page(lang, title, desc, canonical, body, base, crumbs, alts):
    x = TXT[lang]
    other = "en" if lang == "el" else "el"
    home = base if lang == "el" else f"{base}?lang=en"
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]}
    alt_links = "".join(f'<link rel="alternate" hreflang="{k}" href="{esc(v)}">\n' for k, v in alts.items())
    return f"""<!doctype html>
<html lang="{x['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canonical)}">
{alt_links}<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canonical)}">
<meta name="theme-color" content="#0d5eaf">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 30%27%3E%3Cpath d=%27M12 2C8 9 3 13.5 3 19A9 9 0 0 0 21 19C21 13.5 16 9 12 2Z%27 fill=%27%230d5eaf%27/%3E%3Ccircle cx=%2712%27 cy=%2719%27 r=%276.3%27 fill=%27%23ffffff%27/%3E%3Ccircle cx=%2712%27 cy=%2719%27 r=%274.5%27 fill=%27%235aa9e6%27/%3E%3Ccircle cx=%2712%27 cy=%2719%27 r=%272.4%27 fill=%27%230b2d5b%27/%3E%3C/svg%3E">
<script type="application/ld+json">{json_for_script(ld)}</script>
<style>
:root{{--bg:#f6f4ef;--fg:#14232b;--muted:#5d6a70;--line:#e0dcd2;--card:#fdfcf9;--accent:#0d5eaf;--btn:#0d5eaf;--other:#0e9384}}
@media(prefers-color-scheme:dark){{:root{{--bg:#0f1a24;--fg:#e8eef3;--muted:#9db0c1;--line:#263644;--card:#16232f;--accent:#3d9bd8;--btn:#1a6ec2}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
main{{max-width:760px;margin:0 auto;padding:16px}}a{{color:var(--accent)}}
header.top{{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:12px 16px;max-width:760px;margin:0 auto}}
header.top a.brand{{color:var(--fg);text-decoration:none;font-weight:650;display:flex;align-items:center;gap:8px}}
header.top a.sw{{font-size:14px;text-decoration:none;border:1.5px solid var(--line);border-radius:999px;padding:4px 12px;color:var(--fg)}}
nav.crumbs{{font-size:14px;color:var(--muted);margin:4px 0 12px}}nav.crumbs a{{color:var(--muted)}}
h1{{font-size:26px;line-height:1.2;margin:.2em 0 .4em}}h2{{font-size:19px;margin:1.6em 0 .5em}}
.lead{{color:var(--muted);margin:0 0 14px}}
.cta{{display:inline-block;background:var(--btn);color:#fff;text-decoration:none;font-weight:600;padding:10px 16px;border-radius:12px;margin:6px 0 4px}}
.stats{{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0}}.stat{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:8px 14px}}
.stat b{{display:block;font-size:22px}}.stat span{{color:var(--muted);font-size:13px}}
ul.list{{list-style:none;margin:0;padding:0}}ul.list li{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 12px;margin:0 0 8px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}}
ul.list li a.n{{font-weight:600;text-decoration:none}}.badge{{font-size:12px;font-weight:600;padding:1px 8px;border-radius:999px;background:color-mix(in srgb,var(--accent) 14%,transparent);color:var(--accent)}}
.muted{{color:var(--muted);font-size:14px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:8px;list-style:none;padding:0;margin:0}}
.grid a{{display:flex;justify-content:space-between;gap:8px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:9px 12px;text-decoration:none}}
.grid span{{color:var(--muted)}}footer{{max-width:760px;margin:24px auto;padding:0 16px 24px;color:var(--muted);font-size:13px}}
</style>
</head>
<body>
<header class="top"><a class="brand" href="{esc(home)}"><svg viewBox="0 0 24 30" width="17" height="21" aria-hidden="true"><path d="M12 2C8 9 3 13.5 3 19A9 9 0 0 0 21 19C21 13.5 16 9 12 2Z" fill="#0d5eaf"/><circle cx="12" cy="19" r="6.3" fill="#ffffff"/><circle cx="12" cy="19" r="4.5" fill="#5aa9e6"/><circle cx="12" cy="19" r="2.4" fill="#0b2d5b"/></svg>{x['brand']}</a><a class="sw" href="{esc(alts[other])}" hreflang="{other}">{x['switch']}</a></header>
<main>
{body}
</main>
<footer>{esc(x['footer'])}</footer>
</body>
</html>
"""


def main(water_path, areas_path, out_dir, base="https://bestcodereverforsure.github.io/greece-water-map/"):
    base = base if base.endswith("/") else base + "/"
    water = json.load(open(water_path))
    feats, generated = water["features"], water.get("generated", "")
    areas = json.load(open(areas_path))["features"]
    polys = [(shape(a["geometry"]), a["properties"]) for a in areas]
    units = [(g, p) for g, p in polys if p["level"] == "unit"]
    munis = [(g, p) for g, p in polys if p["level"] == "municipality"]
    ut, mt = STRtree([g for g, _ in units]), STRtree([g for g, _ in munis])

    def locate(tree, items, pt):
        for i in tree.query(pt, predicate="within"):
            return items[int(i)][1]["rel"]
        i = tree.nearest(pt)          # coastal points can miss a simplified polygon: accept close ones
        return items[int(i)][1]["rel"] if items[int(i)][0].distance(pt) < 0.004 else None

    by_unit, by_muni, muni_unit = defaultdict(list), defaultdict(list), {}
    for f in feats:
        lon, lat = f["geometry"]["coordinates"]
        pt = Point(lon, lat)
        u, m = locate(ut, units, pt), locate(mt, munis, pt)
        if u: by_unit[u].append(f)
        if m: by_muni[m].append(f)
    for g, p in munis:
        for i in ut.query(g.representative_point(), predicate="within"):
            muni_unit[p["rel"]] = units[int(i)][1]["rel"]
            break

    info, used = {}, set()                 # unique slugs; municipalities keep the plain name when a unit shares it
    for g, p in munis + units:
        el, en, sl = names(p)
        if sl in used and p["level"] == "unit":
            sl = f"{sl}-regional-unit"
        if sl in used:
            sl = f"{sl}-{p['rel']}"
        used.add(sl)
        info[p["rel"]] = {"el": el, "en": en, "slug": sl, "level": p["level"]}

    def area_url(rel, lang):
        return f"{base}{DIRS[lang]}/{info[rel]['slug']}/"

    def index_url(lang):
        return f"{base}{DIRS[lang]}/"

    def map_link(lang, lat, lon, z):
        return f"{base}{'' if lang == 'el' else '?lang=en'}#{z}/{lat:.5f}/{lon:.5f}"

    def counts(fs):
        drink = sum(1 for f in fs if f["properties"]["kind"] == "fountain" or f["properties"].get("drinking_water") == "yes")
        return len(fs), drink

    def point_li(lang, f):
        x = TXT[lang]; p, (lon, lat) = f["properties"], f["geometry"]["coordinates"]
        nm = p.get("name:el") if lang == "el" else (p.get("name:en") or p.get("name"))
        nm = nm or p.get("name") or x["kinds"].get(p["kind"], x["fallback_point"])
        bits = [f'<a class="n" href="{esc(map_link(lang, lat, lon, 18))}">{esc(nm)}</a>',
                f'<span class="muted">{esc(x["kinds"].get(p["kind"], ""))}</span>']
        if p.get("fee") == "no": bits.append(f'<span class="badge">{esc(x["free"])}</span>')
        if p.get("bottle") == "yes": bits.append(f'<span class="badge">{esc(x["bottle"])}</span>')
        return "<li>" + " ".join(bits) + "</li>"

    def order(fs):
        return sorted(fs, key=lambda f: (0 if (f["properties"].get("name:el") or f["properties"].get("name")) else 1,
                                         0 if f["properties"]["kind"] == "fountain" else 1))

    files, urls = {}, []                   # relative path -> content ; URLs for the sitemap

    def area_page(lang, rel, fs):
        x, a = TXT[lang], info[rel]
        name = a[lang]
        total, drink = counts(fs)
        lats = [f["geometry"]["coordinates"][1] for f in fs]; lons = [f["geometry"]["coordinates"][0] for f in fs]
        clat, clon = sum(lats) / len(lats), sum(lons) / len(lons)
        z = 12 if a["level"] == "unit" else 14
        if lang == "el":
            where = "στην " + name if a["level"] == "unit" else "στον " + name.replace("Δήμος ", "Δήμο ", 1)   # accusative after the preposition
            title = f"Πόσιμο νερό και βρύσες: {name} | Νεράκι"
            desc = f"{total} γνωστά σημεία με πόσιμο νερό (βρύσες, κάνουλες, πηγές) {where}. Λίστα και χάρτης, με δεδομένα από το OpenStreetMap."
            h1 = f"Πόσιμο νερό: {name}"
            lead = f"{total} γνωστά σημεία {where}, από τα οποία {drink} δηλώνονται ως πόσιμο νερό στα δεδομένα του χάρτη."
            h_points = f"Σημεία στον χάρτη ({min(total, MAX_LISTED)}{' από ' + str(total) if total > MAX_LISTED else ''})"
            miss = (f'Ξέρεις μια βρύση ή πηγή που δεν φαίνεται εδώ, ή μία που δεν δουλεύει; <a href="{esc(map_link(lang, clat, clon, 16))}">Άνοιξε τον χάρτη</a> '
                    f'και πάτα «Λείπει βρύση;» για να το αναφέρεις. Τα δεδομένα ενημερώνονται κάθε εβδομάδα'
                    f'{(" (τελευταία ενημέρωση: " + esc(generated) + ")") if generated else ""}.')
        else:
            title = f"Drinking water and fountains in {name} | Neraki"
            desc = f"{total} known drinking-water points (fountains, taps, springs) in {name}. List and map, with data from OpenStreetMap."
            h1 = f"Drinking water: {name}"
            lead = f"{total} known points in {name}, {drink} of them marked as drinking water in the map data."
            h_points = f"Points on the map ({min(total, MAX_LISTED)}{' of ' + str(total) if total > MAX_LISTED else ''})"
            miss = (f'Know a fountain or spring that isn\'t shown here, or one that doesn\'t work? <a href="{esc(map_link(lang, clat, clon, 16))}">Open the map</a> '
                    f'and tap “Missing a fountain?” to report it. The data is refreshed every week'
                    f'{(" (last update: " + esc(generated) + ")") if generated else ""}.')
        parent = muni_unit.get(rel) if a["level"] == "municipality" else None
        crumbs = [(x["brand"], base if lang == "el" else base + "?lang=en"), (x["areas"], index_url(lang))]
        crumb_html = f'<a href="{esc(crumbs[0][1])}">{x["brand"]}</a> › <a href="{esc(index_url(lang))}">{x["areas"]}</a>'
        if parent and parent in info:
            crumbs.append((info[parent][lang], area_url(parent, lang)))
            crumb_html += f' › <a href="{esc(area_url(parent, lang))}">{esc(info[parent][lang])}</a>'
        crumbs.append((name, area_url(rel, lang)))
        crumb_html += f" › {esc(name)}"
        body = f"""<nav class="crumbs">{crumb_html}</nav>
<h1>{esc(h1)}</h1>
<p class="lead">{esc(lead)}</p>
<a class="cta" href="{esc(map_link(lang, clat, clon, z))}">{x['open_map']}</a>
<div class="stats"><div class="stat"><b>{total}</b><span>{x['s_total']}</span></div><div class="stat"><b>{drink}</b><span>{x['s_drink']}</span></div><div class="stat"><b>{total - drink}</b><span>{x['s_other']}</span></div></div>
"""
        sib_html = ""
        if a["level"] == "unit":
            kids = [k for k in muni_unit if muni_unit[k] == rel and len(by_muni.get(k, [])) >= MIN_POINTS]
            kids.sort(key=lambda k: -len(by_muni[k]))
            if kids:
                body += f'<h2>{x["h_munis"]}</h2><ul class="grid">' + "".join(
                    f'<li><a href="{esc(area_url(k, lang))}">{esc(info[k][lang])}<span>{len(by_muni[k])}</span></a></li>' for k in kids) + "</ul>"
        else:
            sib = [k for k in muni_unit if muni_unit[k] == parent and k != rel and len(by_muni.get(k, [])) >= MIN_POINTS]
            sib.sort(key=lambda k: -len(by_muni[k]))
            sib_html = "".join(f'<li><a href="{esc(area_url(k, lang))}">{esc(info[k][lang])}<span>{len(by_muni[k])}</span></a></li>' for k in sib[:10])
        body += f'<h2>{esc(h_points)}</h2><ul class="list">' + "".join(point_li(lang, f) for f in order(fs)[:MAX_LISTED]) + "</ul>"
        if sib_html:
            body += f'<h2>{x["h_neigh"]}</h2><ul class="grid">{sib_html}</ul>'
        body += f'<h2>{x["h_missing"]}</h2><p>{miss}</p>'
        alts = {"el": area_url(rel, "el"), "en": area_url(rel, "en"), "x-default": area_url(rel, "el")}
        files[f"{DIRS[lang]}/{a['slug']}/index.html"] = page(lang, title, desc, area_url(rel, lang), body, base, crumbs, alts)
        urls.append(area_url(rel, lang))

    made = 0
    for rel in info:
        fs = by_unit.get(rel, []) if info[rel]["level"] == "unit" else by_muni.get(rel, [])
        if len(fs) >= MIN_POINTS:
            for lang in ("el", "en"):
                area_page(lang, rel, fs)
            made += 1

    total_pts = len(feats)
    unit_rows = [(rel, info[rel]) for rel in info if info[rel]["level"] == "unit" and len(by_unit.get(rel, [])) >= MIN_POINTS]
    for lang in ("el", "en"):
        x = TXT[lang]
        rows = sorted(unit_rows, key=lambda kv: kv[1][lang])
        home = base if lang == "el" else base + "?lang=en"
        if lang == "el":
            title, desc = "Πόσιμο νερό στην Ελλάδα ανά περιοχή | Νεράκι", f"{total_pts} βρύσες, κάνουλες και πηγές πόσιμου νερού στην Ελλάδα, ανά περιφερειακή ενότητα και δήμο."
            h1 = "Πόσιμο νερό στην Ελλάδα, ανά περιοχή"
            lead = f"{total_pts} γνωστά σημεία με βρύσες, κάνουλες και πηγές, ταξινομημένα ανά περιφερειακή ενότητα και δήμο. Δεδομένα από το OpenStreetMap, ενημερωμένα κάθε εβδομάδα."
            h2 = "Περιφερειακές ενότητες"
        else:
            title, desc = "Drinking water in Greece by area | Neraki", f"{total_pts} drinking fountains, taps and springs in Greece, by regional unit and municipality."
            h1 = "Drinking water in Greece, by area"
            lead = f"{total_pts} known fountains, taps and springs, sorted by regional unit and municipality. Data from OpenStreetMap, refreshed every week."
            h2 = "Regional units"
        body = (f'<nav class="crumbs"><a href="{esc(home)}">{x["brand"]}</a> › {x["areas"]}</nav>\n<h1>{esc(h1)}</h1>\n<p class="lead">{esc(lead)}</p>\n'
                f'<a class="cta" href="{esc(home)}">{x["open_map_full"]}</a>\n<h2>{h2}</h2>\n<ul class="grid">'
                + "".join(f'<li><a href="{esc(area_url(r, lang))}">{esc(v[lang])}<span>{len(by_unit[r])}</span></a></li>' for r, v in rows) + "</ul>")
        alts = {"el": index_url("el"), "en": index_url("en"), "x-default": index_url("el")}
        files[f"{DIRS[lang]}/index.html"] = page(lang, title, desc, index_url(lang), body, base, [(x["brand"], home), (x["areas"], index_url(lang))], alts)
        urls.append(index_url(lang))

    for rel_path, content in files.items():
        full = os.path.join(out_dir, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "w").write(content)
    open(os.path.join(out_dir, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{esc(u)}</loc></url>\n" for u in [base] + sorted(urls)) + "</urlset>\n")
    open(os.path.join(out_dir, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {base}sitemap.xml\n")
    print(f"{made} areas x 2 languages = {len(files)} pages (with indexes); {len(urls) + 1} URLs in sitemap; "
          f"points outside every municipality: {len(feats) - sum(len(v) for v in by_muni.values())}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
