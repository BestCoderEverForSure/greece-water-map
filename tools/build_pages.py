"""Generate static, search-engine-friendly pages: one per Greek regional unit and municipality.

Usage: python build_pages.py water.geojson areas.geojson OUT_DIR [BASE_URL]
Writes OUT_DIR/vryses/<slug>/index.html, OUT_DIR/vryses/index.html, OUT_DIR/sitemap.xml, OUT_DIR/robots.txt.
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


def translit(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("ου", "ou").replace("γγ", "ng").replace("γκ", "gk")
    return "".join(GREEK.get(c, c) for c in s)


def slugify(s):
    s = translit(s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "area"


def clean_name(pr):
    """Greek display name and a Latin slug source."""
    el = pr["name_el"] or pr["name"]
    en = pr["name_en"]
    base = re.sub(r"\b(Municipality of|Regional Unit|Regional unit|Municipality)\b", "", en).strip() if en else ""
    if not base:
        base = re.sub(r"^(Δήμος|Περιφερειακή Ενότητα)\s+", "", el)
    return el, slugify(base)


def esc(x):
    return html.escape(str(x), quote=True)


KIND_EL = {"fountain": "Βρύση", "tap": "Κάνουλα", "spring": "Πηγή", "point": "Σημείο νερού"}


def page(title, desc, canonical, body, base, crumbs):
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]}
    return f"""<!doctype html>
<html lang="el">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canonical)}">
<meta name="theme-color" content="#0d5eaf">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 30%27%3E%3Cpath d=%27M12 2C8 9 3 13.5 3 19A9 9 0 0 0 21 19C21 13.5 16 9 12 2Z%27 fill=%27%230d5eaf%27/%3E%3Ccircle cx=%2712%27 cy=%2719%27 r=%276.3%27 fill=%27%23ffffff%27/%3E%3Ccircle cx=%2712%27 cy=%2719%27 r=%274.5%27 fill=%27%235aa9e6%27/%3E%3Ccircle cx=%2712%27 cy=%2719%27 r=%272.4%27 fill=%27%230b2d5b%27/%3E%3C/svg%3E">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>
:root{{--bg:#f6f4ef;--fg:#14232b;--muted:#5d6a70;--line:#e0dcd2;--card:#fdfcf9;--accent:#0d5eaf;--other:#0e9384}}
@media(prefers-color-scheme:dark){{:root{{--bg:#0f1a24;--fg:#e8eef3;--muted:#9db0c1;--line:#263644;--card:#16232f;--accent:#3d9bd8}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
main{{max-width:760px;margin:0 auto;padding:16px}}a{{color:var(--accent)}}
header.top{{display:flex;align-items:center;gap:10px;padding:12px 16px;max-width:760px;margin:0 auto}}
header.top a{{color:var(--fg);text-decoration:none;font-weight:650;display:flex;align-items:center;gap:8px}}
nav.crumbs{{font-size:14px;color:var(--muted);margin:4px 0 12px}}nav.crumbs a{{color:var(--muted)}}
h1{{font-size:26px;line-height:1.2;margin:.2em 0 .4em}}h2{{font-size:19px;margin:1.6em 0 .5em}}
.lead{{color:var(--muted);margin:0 0 14px}}
.cta{{display:inline-block;background:var(--accent);color:#fff;text-decoration:none;font-weight:600;padding:10px 16px;border-radius:12px;margin:6px 0 4px}}
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
<header class="top"><a href="{esc(base)}"><svg viewBox="0 0 24 30" width="17" height="21" aria-hidden="true"><path d="M12 2C8 9 3 13.5 3 19A9 9 0 0 0 21 19C21 13.5 16 9 12 2Z" fill="#0d5eaf"/><circle cx="12" cy="19" r="6.3" fill="#ffffff"/><circle cx="12" cy="19" r="4.5" fill="#5aa9e6"/><circle cx="12" cy="19" r="2.4" fill="#0b2d5b"/></svg>Νεράκι</a></header>
<main>
{body}
</main>
<footer>Τα δεδομένα είναι από το OpenStreetMap, έναν ανοιχτό χάρτη που φτιάχνουν εθελοντές (© OpenStreetMap contributors, ODbL). Το νερό δεν είναι εγγυημένα ασφαλές: οι πληροφορίες προέρχονται από εθελοντές και δεν έχουν ελεγχθεί από εμάς. Αν δεν είσαι σίγουρος, ρώτα ή πάρε δικό σου νερό.</footer>
</body>
</html>
"""


def main(water_path, areas_path, out_dir, base="https://bestcodereverforsure.github.io/greece-water-map/"):
    base = base if base.endswith("/") else base + "/"
    feats = json.load(open(water_path))["features"]
    generated = json.load(open(water_path)).get("generated", "")
    areas = json.load(open(areas_path))["features"]
    polys = [(shape(a["geometry"]), a["properties"]) for a in areas]
    units = [(g, p) for g, p in polys if p["level"] == "unit"]
    munis = [(g, p) for g, p in polys if p["level"] == "municipality"]
    ut, mt = STRtree([g for g, _ in units]), STRtree([g for g, _ in munis])

    def locate(tree, items, pt):
        for i in tree.query(pt, predicate="within"):
            return items[int(i)][1]["rel"]
        i = tree.nearest(pt)          # points on the coast can miss a simplified polygon: accept close ones
        return items[int(i)][1]["rel"] if items[int(i)][0].distance(pt) < 0.004 else None

    by_unit, by_muni = defaultdict(list), defaultdict(list)
    muni_unit = {}
    for f in feats:
        lon, lat = f["geometry"]["coordinates"]
        pt = Point(lon, lat)
        u, m = locate(ut, units, pt), locate(mt, munis, pt)
        if u: by_unit[u].append(f)
        if m: by_muni[m].append(f)
    for g, p in munis:
        rp = g.representative_point()
        for i in ut.query(rp, predicate="within"):
            muni_unit[p["rel"]] = units[int(i)][1]["rel"]
            break

    # slugs (unique)
    info, used = {}, set()
    for g, p in munis + units:            # municipalities first: they keep the plain name when a unit shares it
        el, sl = clean_name(p)
        if sl in used and p["level"] == "unit":
            sl = f"{sl}-regional-unit"
        if sl in used:
            sl = f"{sl}-{p['rel']}"
        used.add(sl)
        info[p["rel"]] = {"el": el, "slug": sl, "level": p["level"], "geom": g}

    def counts(fs):
        drink = sum(1 for f in fs if f["properties"].get("grade") == "drink" or f["properties"]["kind"] == "fountain"
                    or f["properties"].get("drinking_water") == "yes")
        return len(fs), drink

    def area_url(rel):
        return f"{base}vryses/{info[rel]['slug']}/"

    def map_link(lat, lon, z):
        return f"{base}#{z}/{lat:.5f}/{lon:.5f}"

    def point_li(f):
        p, (lon, lat) = f["properties"], f["geometry"]["coordinates"]
        name = p.get("name:el") or p.get("name") or KIND_EL.get(p["kind"], "Σημείο")
        label = name if (p.get("name:el") or p.get("name")) else name
        bits = [f'<a class="n" href="{esc(map_link(lat, lon, 18))}">{esc(label)}</a>']
        bits.append(f'<span class="muted">{esc(KIND_EL.get(p["kind"], ""))}</span>')
        if p.get("fee") == "no": bits.append('<span class="badge">Δωρεάν</span>')
        if p.get("bottle") == "yes": bits.append('<span class="badge">Γέμισμα μπουκαλιού</span>')
        return "<li>" + " ".join(bits) + "</li>"

    def order(fs):
        return sorted(fs, key=lambda f: (0 if (f["properties"].get("name:el") or f["properties"].get("name")) else 1,
                                         0 if f["properties"]["kind"] == "fountain" else 1))

    urls, made = [base, f"{base}vryses/"], 0
    root = os.path.join(out_dir, "vryses")
    os.makedirs(root, exist_ok=True)

    def write(rel_path, content):
        d = os.path.join(root, rel_path) if rel_path else root
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w").write(content)

    def area_page(rel, fs):
        a = info[rel]; total, drink = counts(fs)
        lats = [f["geometry"]["coordinates"][1] for f in fs]; lons = [f["geometry"]["coordinates"][0] for f in fs]
        clat, clon = sum(lats) / len(lats), sum(lons) / len(lons)
        z = 12 if a["level"] == "unit" else 14
        kind_name = "στην " + a["el"] if a["level"] == "unit" else "στον " + a["el"]
        title = f"Πόσιμο νερό και βρύσες: {a['el']} | Νεράκι"
        desc = f"{total} γνωστά σημεία με πόσιμο νερό (βρύσες, κάνουλες, πηγές) {kind_name}. Λίστα και χάρτης, με δεδομένα από το OpenStreetMap."
        crumbs = [("Νεράκι", base), ("Περιοχές", f"{base}vryses/")]
        crumb_html = f'<a href="{esc(base)}">Νεράκι</a> › <a href="{esc(base)}vryses/">Περιοχές</a>'
        parent = muni_unit.get(rel) if a["level"] == "municipality" else None
        if parent and parent in info:
            crumbs.append((info[parent]["el"], area_url(parent)))
            crumb_html += f' › <a href="{esc(area_url(parent))}">{esc(info[parent]["el"])}</a>'
        crumbs.append((a["el"], area_url(rel)))
        crumb_html += f" › {esc(a['el'])}"
        listed = order(fs)[:MAX_LISTED]
        body = f"""<nav class="crumbs">{crumb_html}</nav>
<h1>Πόσιμο νερό: {esc(a['el'])}</h1>
<p class="lead">{total} γνωστά σημεία {esc(kind_name)}, από τα οποία {drink} δηλώνονται ως πόσιμο νερό στα δεδομένα του χάρτη.</p>
<a class="cta" href="{esc(map_link(clat, clon, z))}">Άνοιγμα στον χάρτη</a>
<div class="stats"><div class="stat"><b>{total}</b><span>σημεία συνολικά</span></div><div class="stat"><b>{drink}</b><span>πόσιμο νερό</span></div><div class="stat"><b>{total - drink}</b><span>πηγές και κάνουλες (μη επιβεβαιωμένες)</span></div></div>
"""
        if a["level"] == "unit":
            kids = [(k, info[k]) for k in muni_unit if muni_unit[k] == rel and len(by_muni.get(k, [])) >= MIN_POINTS]
            kids.sort(key=lambda kv: -len(by_muni[kv[0]]))
            if kids:
                body += "<h2>Δήμοι</h2><ul class=\"grid\">" + "".join(
                    f'<li><a href="{esc(area_url(k))}">{esc(v["el"])}<span>{len(by_muni[k])}</span></a></li>' for k, v in kids) + "</ul>"
        else:
            sib = [k for k in muni_unit if muni_unit[k] == parent and k != rel and len(by_muni.get(k, [])) >= MIN_POINTS]
            sib.sort(key=lambda k: -len(by_muni[k]))
            sib_html = "".join(f'<li><a href="{esc(area_url(k))}">{esc(info[k]["el"])}<span>{len(by_muni[k])}</span></a></li>' for k in sib[:10])
        body += f"<h2>Σημεία στον χάρτη ({len(listed)}{' από ' + str(total) if total > len(listed) else ''})</h2><ul class=\"list\">" + "".join(point_li(f) for f in listed) + "</ul>"
        if a["level"] == "municipality" and sib_html:
            body += f'<h2>Γειτονικοί δήμοι στην ίδια ενότητα</h2><ul class="grid">{sib_html}</ul>'
        body += f'<h2>Λείπει κάποια βρύση;</h2><p>Ξέρεις μια βρύση ή πηγή που δεν φαίνεται εδώ, ή μία που δεν δουλεύει; <a href="{esc(map_link(clat, clon, 16))}">Άνοιξε τον χάρτη</a> και πάτα «Λείπει βρύση;» για να το αναφέρεις. Τα δεδομένα ενημερώνονται κάθε εβδομάδα{(" (τελευταία ενημέρωση: " + esc(generated) + ")") if generated else ""}.</p>'
        write(a["slug"], page(title, desc, area_url(rel), body, base, crumbs))
        urls.append(area_url(rel))

    for rel in info:
        fs = by_unit.get(rel, []) if info[rel]["level"] == "unit" else by_muni.get(rel, [])
        if len(fs) >= MIN_POINTS:
            area_page(rel, fs); made += 1

    # index page
    unit_rows = sorted(((rel, info[rel]) for rel in info if info[rel]["level"] == "unit" and len(by_unit.get(rel, [])) >= MIN_POINTS),
                       key=lambda kv: kv[1]["el"])
    total_pts = len(feats)
    idx_body = f"""<nav class="crumbs"><a href="{esc(base)}">Νεράκι</a> › Περιοχές</nav>
<h1>Πόσιμο νερό στην Ελλάδα, ανά περιοχή</h1>
<p class="lead">{total_pts} γνωστά σημεία με βρύσες, κάνουλες και πηγές, ταξινομημένα ανά περιφερειακή ενότητα και δήμο. Δεδομένα από το OpenStreetMap, ενημερωμένα κάθε εβδομάδα.</p>
<a class="cta" href="{esc(base)}">Άνοιγμα του χάρτη</a>
<h2>Περιφερειακές ενότητες</h2>
<ul class="grid">""" + "".join(f'<li><a href="{esc(area_url(r))}">{esc(v["el"])}<span>{len(by_unit[r])}</span></a></li>' for r, v in unit_rows) + "</ul>"
    open(os.path.join(root, "index.html"), "w").write(page(
        "Πόσιμο νερό στην Ελλάδα ανά περιοχή | Νεράκι",
        f"{total_pts} βρύσες, κάνουλες και πηγές πόσιμου νερού στην Ελλάδα, ανά περιφερειακή ενότητα και δήμο.",
        f"{base}vryses/", idx_body, base, [("Νεράκι", base), ("Περιοχές", f"{base}vryses/")]))

    open(os.path.join(out_dir, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{esc(u)}</loc></url>\n" for u in urls) + "</urlset>\n")
    open(os.path.join(out_dir, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {base}sitemap.xml\n")
    print(f"{made} area pages + index; {len(urls)} URLs in sitemap; points outside every municipality: "
          f"{len(feats) - sum(len(v) for v in by_muni.values())}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
