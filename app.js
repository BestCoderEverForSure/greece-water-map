"use strict";
// Optional integrations. Fill these in to switch them on (empty = off).
const DONATE_URL = "https://ko-fi.com/turbowater";   // e.g. a Ko-fi or GitHub Sponsors page
const startedWithHash = location.hash.length > 1;

const T = {
  el: {
    title: "Νεράκι", ok: "ΟΚ", cancel: "Άκυρο",
    gDrink: "Πόσιμο νερό", gOther: "Πηγές & κάνουλες",
    fountain: "Βρύση", tap: "Κάνουλα", spring: "Πηγή", point: "Σημείο νερού", bottle: "Γέμισμα μπουκαλιού", free: "Δωρεάν",
    menuPlaces: "Μέρη", menuMap: "Τύπος χάρτη", menuAreas: "Λίστα ανά περιοχή", menuInstall: "Εγκατάσταση εφαρμογής", offline: "Χωρίς σύνδεση. Δείχνουμε τα δεδομένα που έχουν αποθηκευτεί.", dataFail: "Δεν φόρτωσαν τα σημεία. Έλεγξε τη σύνδεση και ξαναδοκίμασε.", retry: "Ξαναδοκίμασε", stillLoading: "Τα σημεία φορτώνουν ακόμα. Δοκίμασε ξανά σε λίγο.", gpxTooBig: "Το αρχείο είναι πολύ μεγάλο (όριο 25 MB).", online: "Ξανά online.", iosTip: "Στο iPhone: Κοινοποίηση, μετά «Προσθήκη στην αρχική οθόνη».", edit: "Επεξεργασία", menuShare: "Κοινοποίηση", copied: "Ο σύνδεσμος αντιγράφηκε", theme: "Θέμα", theme_auto: "Αυτόματο", theme_light: "Φωτεινό", theme_dark: "Σκούρο", mapStandard: "Κανονικός", mapTerrain: "Ανάγλυφο", mapTerrainNote: "Σκιασμένο ανάγλυφο, καλό για βουνά και πεζοπορία.", mapSat: "Δορυφόρος", mapSatNote: "Sentinel-2, 2016, περίπου 10 μ. ανάλυση. Καλός για βουνά και βλάστηση, όχι για λεπτομέρειες δρόμων.", route: "Διαδρομή GPX", menuAbout: "Σχετικά", menuSupport: "Στήριξη",
    placesTitle: "Μετάβαση σε μέρος", placesSearch: "Αναζήτηση…", pts: n => `${n} σημεία`,
    legendDrink: "Πόσιμο νερό: σημεία που εθελοντές του χάρτη έχουν σημειώσει ως πόσιμο νερό.",
    legendOther: "Πηγές και κάνουλες: δεν αναφέρεται αν το νερό είναι πόσιμο. Έλεγξε πριν πιεις.",
    missing: "Λείπει βρύση;", missingTitle: "Λείπει μια βρύση;", missingGo: "Άνοιγμα σημείωσης",
    missingBody: "Θα ανοίξει μια σημείωση στο OpenStreetMap (ο ανοιχτός χάρτης από τον οποίο παίρνουμε τα δεδομένα) στο σημείο που βλέπεις τώρα στον χάρτη. Πρώτα μετακίνησε τον χάρτη πάνω στο σημείο. Στη σημείωση γράψε τι είναι (βρύση, κάνουλα, πηγή), πού ακριβώς βρίσκεται και αν τρέχει νερό.",
    sparse: n => n === 0 ? "Δεν έχουμε κανένα σημείο εδώ. Ξέρεις κάποιο;" : `Μόνο ${n} ${n === 1 ? "σημείο" : "σημεία"} εδώ. Ξέρεις κάποιο που λείπει;`, sparseCta: "Πρόσθεσε",
    nearest: "Πιο κοντινές σε σένα", nearestMap: "Πιο κοντινές στο κέντρο του χάρτη", nearestNone: "Δεν βρέθηκε τίποτα εδώ. Μετακίνησε τον χάρτη.", useLocation: "Χρήση της τοποθεσίας μου", min: "λεπ.",
    noResults: "Δεν βρέθηκε τίποτα κοντά σου με αυτά τα φίλτρα.",
    locFail: "Δεν βρέθηκε η τοποθεσία σου. Έλεγξε τα δικαιώματα του browser.",
    outside: "Φαίνεται ότι είσαι εκτός Ελλάδας. Δείχνουμε την Αθήνα.",
    points: n => n.toLocaleString("el") + " σημεία",
    drinkable: "Νερό", drinkableYes: "σημειωμένο ως πόσιμο από εθελοντές, δεν έχει ελεγχθεί", drinkableListed: "σημειωμένο ως πόσιμο από εθελοντές, δεν έχει ελεγχθεί", drinkableUnknown: "δεν αναφέρεται αν είναι πόσιμο",
    seasonal: "Εποχιακό", fee: "Χρέωση", hours: "Ώρες", note: "Σημείωση", checked: "Τελευταίος έλεγχος", away: "από εσένα",
    viewOsm: "Περισσότερες λεπτομέρειες", report: "Πρόβλημα / λείπει κάτι;", directions: "Οδηγίες", streetView: "Street View", km: "χλμ", m: "μ",
    routeTitle: "Κατά μήκος της διαδρομής", within: "Απόσταση:", clearRoute: "Καθαρισμός", routeErr: "Δεν βρέθηκε διαδρομή σε αυτό το αρχείο GPX.",
    routeNone: "Δεν βρέθηκαν σημεία κοντά στη διαδρομή. Πάρε νερό μαζί σου.", routeNote: "Μετράει μόνο σημεία που ξέρουμε, ίσως υπάρχουν κι άλλα.",
    routeSum: (len, n, gap) => `${len} χλμ · ${n} σημεία · Μεγαλύτερο διάστημα χωρίς νερό: ${gap} χλμ`,
    aboutTitle: "Για τον χάρτη",
    aboutBody: "Δείχνει βρύσες, κάνουλες και πηγές στην Ελλάδα. Τα δεδομένα είναι από το OpenStreetMap, έναν ανοιχτό χάρτη που φτιάχνουν εθελοντές, και τα ενημερώνουμε τακτικά. Δεν είναι πλήρη: σε πολλές πόλεις λείπουν σημεία.",
    aboutSafety: "Το νερό δεν είναι εγγυημένα ασφαλές. Οι πληροφορίες είναι από εθελοντές και δεν ελέγχονται από εμάς. Αν δεν είσαι σίγουρος, ρώτα ή πάρε δικό σου νερό.",
    aboutMissing: "Βρήκες μια βρύση που λείπει ή δεν δουλεύει; Πάτα «Λείπει βρύση;» ή «Πρόβλημα / λείπει κάτι;» σε ένα σημείο.",
    privacy: "Η τοποθεσία σου και τα αρχεία GPX μένουν στη συσκευή σου και δεν ανεβαίνουν πουθενά. Ο χάρτης φορτώνει από το OpenFreeMap (και, αν τα επιλέξεις, ανάγλυφο από την AWS και δορυφορικές εικόνες από την EOX), οπότε αυτοί βλέπουν τη διεύθυνση IP σου, όπως με κάθε ιστοσελίδα.",
    mapLabel: "Χάρτης με σημεία πόσιμου νερού", langLabel: "Switch to English", menuLabel: "Μενού",
    updated: "Δεδομένα από", donate: "Σου αρέσει ο χάρτης; Κέρασε έναν καφέ", statsNote: "Μετράμε τις επισκέψεις με το Cloudflare Web Analytics, χωρίς cookies και χωρίς να σε παρακολουθούμε σε άλλες σελίδες.", feedback: "Σχόλια ή προβλήματα στη σελίδα",
  },
  en: {
    title: "Νεράκι", ok: "OK", cancel: "Cancel",
    gDrink: "Drinking water", gOther: "Springs & taps",
    fountain: "Fountain", tap: "Tap", spring: "Spring", point: "Water point", bottle: "Bottle refill", free: "Free",
    menuPlaces: "Places", menuMap: "Map type", menuAreas: "Browse by area", menuInstall: "Install app", offline: "You're offline. Showing saved data.", dataFail: "The points didn't load. Check your connection and try again.", retry: "Try again", stillLoading: "The points are still loading. Try again in a moment.", gpxTooBig: "That file is too large (limit 25 MB).", online: "Back online.", iosTip: "On iPhone: Share, then “Add to Home Screen”.", edit: "Edit", menuShare: "Share", copied: "Link copied", theme: "Theme", theme_auto: "Auto", theme_light: "Light", theme_dark: "Dark", mapStandard: "Standard", mapTerrain: "Terrain", mapTerrainNote: "Shaded relief, good for mountains and hiking.", mapSat: "Satellite", mapSatNote: "Sentinel-2, 2016, about 10 m resolution. Good for mountains and vegetation, not for street details.", route: "Route (GPX)", menuAbout: "About", menuSupport: "Support",
    placesTitle: "Jump to a place", placesSearch: "Search…", pts: n => `${n} points`,
    legendDrink: "Drinking water: points that map volunteers have marked as drinking water.",
    legendOther: "Springs and taps: it isn't stated whether the water is drinkable. Check before you drink.",
    missing: "Missing a fountain?", missingTitle: "Missing a fountain?", missingGo: "Open note",
    missingBody: "This opens a note on OpenStreetMap (the open map our data comes from) at the spot you see on the map now. First move the map onto the spot. In the note, say what it is (fountain, tap, spring), exactly where it is, and whether water flows.",
    sparse: n => n === 0 ? "No points here yet. Know one?" : `Only ${n} ${n === 1 ? "point" : "points"} here. Know one that's missing?`, sparseCta: "Add",
    nearest: "Nearest to you", nearestMap: "Nearest to the map centre", nearestNone: "Nothing found here. Move the map.", useLocation: "Use my location", min: "min",
    noResults: "Nothing found near you with these filters.",
    locFail: "Couldn't get your location. Check your browser permissions.",
    outside: "You seem to be outside Greece. Showing Athens.",
    points: n => n.toLocaleString("en") + " points",
    drinkable: "Water", drinkableYes: "marked as drinking water by volunteers, not verified", drinkableListed: "marked as drinking water by volunteers, not verified", drinkableUnknown: "not stated whether it's drinkable",
    seasonal: "Seasonal", fee: "Fee", hours: "Hours", note: "Note", checked: "Last checked", away: "away",
    viewOsm: "More details", report: "Problem / missing one?", directions: "Directions", streetView: "Street View", km: "km", m: "m",
    routeTitle: "Along the route", within: "Within:", clearRoute: "Clear", routeErr: "No route found in that GPX file.",
    routeNone: "No points found near this route. Carry water.", routeNote: "Counts only points we know about, more may exist.",
    routeSum: (len, n, gap) => `${len} km · ${n} points · Longest stretch without water: ${gap} km`,
    aboutTitle: "About this map",
    aboutBody: "Shows fountains, taps and springs in Greece. Data is from OpenStreetMap, an open map made by volunteers, and is refreshed regularly. It's incomplete: many towns are missing points.",
    aboutSafety: "Water isn't guaranteed safe. Info comes from volunteers and isn't checked by us. If you're unsure, ask locally or carry your own water.",
    aboutMissing: "Found one that's missing or broken? Tap “Missing a fountain?” or “Problem / missing one?” on a point.",
    privacy: "Your location and GPX files stay on your device and aren't uploaded. The map loads from OpenFreeMap (and, if you choose them, terrain from AWS and satellite images from EOX), so those services see your IP address, as with any website.",
    mapLabel: "Map of drinking water points", langLabel: "Αλλαγή σε ελληνικά", menuLabel: "Menu",
    updated: "Data from", donate: "Like the map? Buy me a coffee", statsNote: "We count visits with Cloudflare Web Analytics, without cookies and without tracking you across sites.", feedback: "Feedback or problems with this page",
  },
};
let lang = (navigator.language || "el").toLowerCase().startsWith("el") ? "el" : "en";
try { lang = localStorage.getItem("lang") || lang; } catch (e) {}
{ const q = new URLSearchParams(location.search).get("lang");   // links from the English area pages open the app in English
  if (q === "el" || q === "en") { lang = q; try { localStorage.setItem("lang", q); } catch (e) {} } }
const t = k => T[lang][k];

// ---- places (centre points are approximate)
const PLACES = [
  ["Αθήνα", "Athens", 37.9838, 23.7275, 13.5], ["Θεσσαλονίκη", "Thessaloniki", 40.6401, 22.9444, 13.5],
  ["Πάτρα", "Patras", 38.2466, 21.7346, 13.5], ["Ηράκλειο", "Heraklion", 35.3387, 25.1442, 13.5],
  ["Χανιά", "Chania", 35.5138, 24.0180, 14], ["Ρέθυμνο", "Rethymno", 35.3660, 24.4790, 14],
  ["Άγιος Νικόλαος", "Agios Nikolaos", 35.1900, 25.7150, 14], ["Ρόδος", "Rhodes", 36.4349, 28.2176, 13.5],
  ["Κως", "Kos", 36.8930, 27.2877, 14], ["Κέρκυρα", "Corfu", 39.6243, 19.9217, 13.5],
  ["Ζάκυνθος", "Zakynthos", 37.7870, 20.8990, 14], ["Αργοστόλι (Κεφαλονιά)", "Argostoli (Kefalonia)", 38.1753, 20.4890, 14],
  ["Λευκάδα", "Lefkada", 38.8300, 20.7000, 14], ["Σαντορίνη (Φηρά)", "Santorini (Fira)", 36.4166, 25.4320, 14],
  ["Μύκονος", "Mykonos", 37.4467, 25.3289, 14], ["Νάξος", "Naxos", 37.1036, 25.3763, 14],
  ["Πάρος (Παροικιά)", "Paros (Parikia)", 37.0850, 25.1500, 14], ["Σύρος (Ερμούπολη)", "Syros (Ermoupoli)", 37.4440, 24.9420, 14],
  ["Μήλος (Αδάμαντας)", "Milos (Adamas)", 36.7240, 24.4410, 14], ["Λέσβος (Μυτιλήνη)", "Lesvos (Mytilene)", 39.1100, 26.5547, 14],
  ["Χίος", "Chios", 38.3700, 26.1350, 14], ["Σάμος (Βαθύ)", "Samos (Vathy)", 37.7550, 26.9770, 14],
  ["Θάσος", "Thasos", 40.7780, 24.7050, 14], ["Σκιάθος", "Skiathos", 39.1620, 23.4900, 14],
  ["Βόλος", "Volos", 39.3610, 22.9420, 13.5], ["Πήλιο (Πορταριά)", "Pelion (Portaria)", 39.3860, 22.9990, 13],
  ["Λάρισα", "Larissa", 39.6390, 22.4191, 13.5], ["Ιωάννινα", "Ioannina", 39.6650, 20.8537, 13.5],
  ["Μετέωρα (Καλαμπάκα)", "Meteora (Kalambaka)", 39.7217, 21.6306, 13], ["Όλυμπος (Λιτόχωρο)", "Mount Olympus (Litochoro)", 40.1040, 22.5010, 13],
  ["Δελφοί", "Delphi", 38.4824, 22.5010, 14], ["Ναύπλιο", "Nafplio", 37.5673, 22.8078, 14],
  ["Κόρινθος", "Corinth", 37.9400, 22.9300, 13.5], ["Ολυμπία", "Olympia", 37.6383, 21.6300, 14],
  ["Σπάρτη", "Sparta", 37.0740, 22.4300, 14], ["Καλαμάτα", "Kalamata", 37.0389, 22.1142, 13.5],
  ["Καβάλα", "Kavala", 40.9397, 24.4019, 13.5], ["Αλεξανδρούπολη", "Alexandroupoli", 40.8457, 25.8744, 13.5],
];
const inGreece = ([lon, lat]) => lat > 34.5 && lat < 42 && lon > 19.2 && lon < 29.8;

// ---- water groups: "drink" = the map data says drinking water; "other" = springs/taps with no drinkability claim
const GROUPS = { drink: false, other: true };            // value = shown as a hollow ring
const active = new Set(Object.keys(GROUPS));
const gradeOf = p => (p.kind === "fountain" || p.drinking_water === "yes") ? "drink" : "other";
let data = null, userPos = null, firstFix = true;

const $ = id => document.getElementById(id);
const sheet = $("sheet");
function setSheet(open) { sheet.classList.toggle("open", open); $("grab").setAttribute("aria-expanded", open); }
let toastTimer;
function toast(msg) { const el = $("toast"); el.textContent = msg; el.classList.add("show"); clearTimeout(toastTimer); toastTimer = setTimeout(() => el.classList.remove("show"), 4500); }

let basemap = "standard";
try { basemap = localStorage.getItem("basemap") || "standard"; } catch (e) {}
if (!["standard", "terrain", "satellite"].includes(basemap)) basemap = "standard";
let theme = "auto";
try { theme = localStorage.getItem("theme") || "auto"; } catch (e) {}
if (!["auto", "light", "dark"].includes(theme)) theme = "auto";
const darkQuery = matchMedia("(prefers-color-scheme: dark)");
const isDark = () => theme === "dark" || (theme === "auto" && darkQuery.matches);
function applyTheme() { if (theme === "auto") document.documentElement.removeAttribute("data-theme"); else document.documentElement.dataset.theme = theme; }
applyTheme();
const styleUrl = () => "https://tiles.openfreemap.org/styles/" + ((isDark() || basemap === "satellite") ? "dark" : "liberty");
const DROP_BLUE = "#0d5eaf", RING = "#0e9384";
const DROP_PATH = "M12 2C8 9 3 13.5 3 19A9 9 0 0 0 21 19C21 13.5 16 9 12 2Z";
function dropSVG(grade, w = 12) {
  const solid = grade !== "other";
  return `<svg class="drop" viewBox="0 0 24 30" width="${w}" height="${Math.round(w * 1.25)}" aria-hidden="true"><path d="${DROP_PATH}" fill="${solid ? DROP_BLUE : "none"}" stroke="${solid ? "#ffffff" : RING}" stroke-width="${solid ? 1.5 : 3}"/></svg>`;
}
function mountDrops() { document.querySelectorAll("[data-drop]").forEach(e => { e.innerHTML = dropSVG(e.dataset.drop, 16); }); }

const map = new maplibregl.Map({
  container: "map",
  style: styleUrl(),
  center: [23.73, 37.98], zoom: 11, hash: true, attributionControl: { compact: true },
});
const geolocate = new maplibregl.GeolocateControl({
  positionOptions: { enableHighAccuracy: true, timeout: 15000 },
  trackUserLocation: true, showUserHeading: true, fitBoundsOptions: { maxZoom: 15 },
});
map.addControl(geolocate, "bottom-right");
map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "bottom-right");
new ResizeObserver(() => map.resize()).observe($("map"));

let wantSheet = false;
geolocate.on("trackuserlocationstart", () => { wantSheet = true; });
geolocate.on("geolocate", e => {
  const p = [e.coords.longitude, e.coords.latitude];
  if (!inGreece(p)) {
    userPos = null;
    if (firstFix || wantSheet) { toast(t("outside")); map.flyTo({ center: [23.7275, 37.9838], zoom: 12 }); }
    firstFix = false;
    if (wantSheet) { renderList(); setSheet(true); wantSheet = false; }   // show the list for the map centre instead
    else renderList();
    return;
  }
  const moved = !userPos || haversine(userPos, p) > 15;
  userPos = p;
  if (moved || firstFix || wantSheet) renderList();   // GPS fixes arrive about once a second; don't rebuild the list for jitter
  if (firstFix || wantSheet) setSheet(true);
  firstFix = false; wantSheet = false;
});
geolocate.on("error", () => { toast(t("locFail")); userPos = null; renderList(); });

function haversine(a, b) {
  const R = 6371000, r = Math.PI / 180;
  const dLat = (b[1] - a[1]) * r, dLon = (b[0] - a[0]) * r;
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(a[1] * r) * Math.cos(b[1] * r) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
}
const fmtDist = d => d < 1000 ? Math.round(d / 10) * 10 + " " + t("m") : (d / 1000).toFixed(d < 10000 ? 1 : 0) + " " + t("km");
const nameOf = p => p["name:" + lang] || p.name || p["name:el"] || p["name:en"] || "";
const labelOf = p => nameOf(p) ? `${t(p.kind)} · ${nameOf(p)}` : t(p.kind);
const visible = f => active.has(f.properties.grade);
const norm = s => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
const GR = { α: "a", β: "v", γ: "g", δ: "d", ε: "e", ζ: "z", η: "i", θ: "th", ι: "i", κ: "k", λ: "l", μ: "m", ν: "n", ξ: "x",
             ο: "o", π: "p", ρ: "r", σ: "s", ς: "s", τ: "t", υ: "y", φ: "f", χ: "ch", ψ: "ps", ω: "o" };
const greeklish = s => norm(s).replace(/ου/g, "ou").replace(/γγ/g, "ng").replace(/γκ/g, "gk").replace(/[α-ω]/g, c => GR[c] || c);

function applyFilter() {
  if (!map.getSource("water")) return;
  // Clusters are computed from the source, so rebuild the source with the filtered data.
  map.getSource("water").setData({ type: "FeatureCollection", features: data.features.filter(visible) });
  if (route) computeHits();
  renderList();
  $("count").textContent = t("points")(data.features.filter(visible).length);
  updateNudge();
}

function renderChips() {
  const box = $("chips"); box.textContent = "";
  for (const [g, ring] of Object.entries(GROUPS)) {
    const b = document.createElement("button");
    b.className = "chip"; b.setAttribute("aria-pressed", active.has(g));
    const i = document.createElement("span"); i.innerHTML = dropSVG(ring ? "other" : "drink", 14);
    b.append(i, document.createTextNode(t(g === "drink" ? "gDrink" : "gOther")));
    b.onclick = () => { active.has(g) ? active.delete(g) : active.add(g); b.setAttribute("aria-pressed", active.has(g)); applyFilter(); };
    box.append(b);
  }
}

function dotFor(p) { const d = document.createElement("span"); d.innerHTML = dropSVG(p.grade, 12); return d; }

function bearing(a, b) {
  const r = Math.PI / 180, dLon = (b[0] - a[0]) * r, y = Math.sin(dLon) * Math.cos(b[1] * r);
  const x = Math.cos(a[1] * r) * Math.sin(b[1] * r) - Math.sin(a[1] * r) * Math.cos(b[1] * r) * Math.cos(dLon);
  return (Math.atan2(y, x) / r + 360) % 360;
}
const walkMin = d => Math.max(1, Math.round(d / 80));   // about 5 km/h

function nearestRef() { const c = map.getCenter(); return userPos || [c.lng, c.lat]; }

function renderList() {
  const ul = $("list"); ul.textContent = "";
  $("rctl").hidden = !route;
  if (route) return renderRouteList(ul);
  const ref = nearestRef();
  $("sheetTitle").textContent = t(userPos ? "nearest" : "nearestMap");
  if (!userPos) {
    const b = document.createElement("button"); b.className = "locbtn"; b.textContent = t("useLocation");
    b.onclick = () => { if (geolocate._watchState === "ACTIVE_LOCK") toast(t("outside")); else geolocate.trigger(); };   // trigger() toggles tracking off when already locked
    ul.append(b);
  }
  const say = txt => { const p = document.createElement("p"); p.className = "empty"; p.textContent = txt; ul.append(p); };
  if (!data) return;
  const near = data.features.filter(visible)
    .map(f => ({ f, d: haversine(ref, f.geometry.coordinates) })).sort((a, b) => a.d - b.d).slice(0, 12);
  if (!near.length) return say(t("nearestNone"));
  $("sheetTitle").textContent += ` · ${fmtDist(near[0].d)}`;      // visible even when the panel is collapsed
  for (const { f, d } of near) {
    const li = document.createElement("li"), b = document.createElement("button");
    const nm = document.createElement("span"); nm.textContent = labelOf(f.properties);
    const arrow = document.createElement("span"); arrow.className = "brg"; arrow.textContent = "↑";
    arrow.style.transform = `rotate(${Math.round(bearing(ref, f.geometry.coordinates))}deg)`; arrow.setAttribute("aria-hidden", "true");
    const ds = document.createElement("span"); ds.className = "dist";
    ds.textContent = d < 5000 ? `${fmtDist(d)} · ${walkMin(d)} ${t("min")}` : fmtDist(d);
    b.append(dotFor(f.properties), nm, ds, arrow); b.onclick = () => { focusOn(f); setSheet(false); };
    li.append(b); ul.append(li);
  }
}
let nearestTimer;
function scheduleNearest() { if (userPos || route) return; clearTimeout(nearestTimer); nearestTimer = setTimeout(renderList, 200); }

function popupNode(f) {
  const p = f.properties, [lon, lat] = f.geometry.coordinates, div = document.createElement("div");
  div.className = "pop";
  const h = document.createElement("h3"); h.textContent = labelOf(p); div.append(h);
  const line = txt => { const e = document.createElement("p"); e.textContent = txt; div.append(e); };
  line(`${t("drinkable")}: ${p.drinking_water === "yes" ? t("drinkableYes") : p.kind === "fountain" ? t("drinkableListed") : t("drinkableUnknown")}`);
  if (userPos) line(`${fmtDist(haversine(userPos, [lon, lat]))} ${t("away")}`);
  const badges = [];
  if (p.fee === "no") badges.push(t("free"));
  if (p.bottle === "yes") badges.push(t("bottle"));
  if (badges.length) {
    const row = document.createElement("div"); row.className = "badges";
    for (const b of badges) { const e = document.createElement("span"); e.className = "badge"; e.textContent = b; row.append(e); }
    div.append(row);
  }
  if (p.seasonal) line(`${t("seasonal")}: ${p.seasonal}`);
  if (p.fee && p.fee !== "no") line(`${t("fee")}: ${p.fee}`);
  if (p.opening_hours) line(`${t("hours")}: ${p.opening_hours}`);
  if (p.check_date) line(`${t("checked")}: ${p.check_date}`);
  if (p.description) line(`${t("note")}: ${p.description}`);
  const links = document.createElement("div"); links.className = "links";
  const mk = (href, txt) => { const a = document.createElement("a"); a.href = href; a.target = "_blank"; a.rel = "noopener"; a.textContent = txt; return a; };
  const kind = p.osm.startsWith("n") ? "node" : "way";
  links.append(mk(`https://www.openstreetmap.org/${kind}/${p.osm.slice(1)}`, t("viewOsm")),
               mk(`https://www.openstreetmap.org/edit?${kind}=${p.osm.slice(1)}`, t("edit")),
               mk(`https://www.openstreetmap.org/note/new#map=19/${lat}/${lon}`, t("report")),
               mk(`https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lon}`, t("streetView")));
  div.append(links);
  const dir = document.createElement("a"); dir.className = "dir"; dir.target = "_blank"; dir.rel = "noopener";
  dir.href = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}&travelmode=walking`;
  dir.textContent = "→ " + t("directions"); div.append(dir);
  return div;
}

let popup = null;
function focusOn(f) {
  // Put the point in the lower part of the screen so the popup above it clears the top bar.
  map.flyTo({ center: f.geometry.coordinates, zoom: Math.max(map.getZoom(), 16), offset: [0, Math.min(170, innerHeight * 0.22)] });
  if (popup) popup.remove();
  popup = new maplibregl.Popup({ offset: { bottom: [0, -30], "bottom-left": [0, -30], "bottom-right": [0, -30], top: [0, 6], "top-left": [0, 6], "top-right": [0, 6], left: [8, -15], right: [-8, -15], center: [0, 0] } }).setLngLat(f.geometry.coordinates).setDOMContent(popupNode(f)).addTo(map);
}

// ---- "missing a fountain?" and the low-coverage nudge
function updateMissingLink() {
  const c = map.getCenter(), z = Math.max(17, Math.round(map.getZoom()));
  $("missingGo").href = `https://www.openstreetmap.org/note/new#map=${z}/${c.lat.toFixed(5)}/${c.lng.toFixed(5)}`;
}
function updateNudge() {
  const z = map.getZoom();
  if (!data || z < 12 || z > 15) { $("nudge").classList.remove("show"); return; }   // street level always looks sparse
  const b = map.getBounds(), w = b.getWest(), e = b.getEast(), s = b.getSouth(), n = b.getNorth();
  const inView = data.features.filter(f => { const [x, y] = f.geometry.coordinates; return visible(f) && x >= w && x <= e && y >= s && y <= n; }).length;
  $("nudgeText").textContent = t("sparse")(inView);
  $("nudge").classList.toggle("show", inView < 8);
}
map.on("moveend", () => { updateMissingLink(); updateNudge(); scheduleNearest(); });
updateMissingLink();
const openMissing = () => { updateMissingLink(); $("mdlg").showModal(); };
$("missing").onclick = openMissing;
$("nudgeBtn").onclick = openMissing;
$("mCancel").onclick = () => $("mdlg").close();
$("missingGo").addEventListener("click", () => $("mdlg").close());

// ---- places
let placeCounts = [];
function countPlaces() {
  placeCounts = PLACES.map(([, , lat, lon]) => data.features.reduce((n, f) => n + (haversine([lon, lat], f.geometry.coordinates) <= 4000 ? 1 : 0), 0));
}
function renderPlaces() {
  const q = norm($("pq").value.trim()), ul = $("plist"); ul.textContent = "";
  PLACES.forEach(([el, en, lat, lon, zoom], i) => {
    if (q && ![norm(el), norm(en), greeklish(el)].some(n => n.includes(q))) return;
    const li = document.createElement("li"), b = document.createElement("button");
    const nm = document.createElement("span"); nm.textContent = lang === "el" ? el : en;
    const n = document.createElement("span"); n.className = "n"; if (data) n.textContent = t("pts")(placeCounts[i] ?? 0);
    b.append(nm, n);
    b.onclick = () => { $("pdlg").close(); map.flyTo({ center: [lon, lat], zoom }); };
    li.append(b); ul.append(li);
  });
}
function openPlaces() { $("pq").value = ""; renderPlaces(); $("pdlg").showModal(); }
$("pq").oninput = renderPlaces;
$("pClose").onclick = () => $("pdlg").close();

// ---- menu
const menuItems = () => [...$("menu").querySelectorAll("button, a")].filter(x => !x.hidden);
function setMenu(open, focusFirst) {
  const wasOpen = !$("menu").hidden;
  $("menu").hidden = !open; $("menuBtn").setAttribute("aria-expanded", open);
  if (open && focusFirst) menuItems()[0]?.focus();
  if (!open && wasOpen && $("menu").contains(document.activeElement)) $("menuBtn").focus();
}
$("menuBtn").onclick = e => { e.stopPropagation(); setMenu($("menu").hidden, e.detail === 0); };   // detail 0 = keyboard activation
document.addEventListener("click", e => { if (!$("menu").hidden && !$("menu").contains(e.target)) setMenu(false); });
document.addEventListener("keydown", e => {
  if ($("menu").hidden) return;
  if (e.key === "Escape") { setMenu(false); $("menuBtn").focus(); return; }
  if (e.key === "ArrowDown" || e.key === "ArrowUp") {
    const items = menuItems(), i = items.indexOf(document.activeElement);
    items[(i + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length]?.focus(); e.preventDefault();
  }
});
$("mPlaces").onclick = () => { setMenu(false); openPlaces(); };
$("mMap").onclick = () => { setMenu(false); document.querySelector(`input[name="bm"][value="${basemap}"]`).checked = true; $("bdlg").showModal(); };
$("mRoute").onclick = () => { setMenu(false); $("gpxIn").click(); };
$("mTheme").onclick = () => {
  theme = { auto: "light", light: "dark", dark: "auto" }[theme];
  try { localStorage.setItem("theme", theme); } catch (e) {}
  applyTheme(); reloadStyle(); applyLang();
};
darkQuery.addEventListener("change", () => { if (theme === "auto") reloadStyle(); });
$("mShare").onclick = async () => {
  setMenu(false);
  try {
    if (navigator.share) await navigator.share({ title: document.title, url: location.href });
    else { await navigator.clipboard.writeText(location.href); toast(t("copied")); }
  } catch (e) {}
};
$("mAbout").onclick = () => { setMenu(false); $("dlg").showModal(); };
$("mSupport").onclick = () => setMenu(false);
let installEvt = null;
addEventListener("beforeinstallprompt", e => { e.preventDefault(); installEvt = e; $("mInstall").hidden = false; });
addEventListener("appinstalled", () => { installEvt = null; $("mInstall").hidden = true; });
$("mInstall").onclick = async () => {
  setMenu(false);
  if (!installEvt) return;
  installEvt.prompt();
  try { await installEvt.userChoice; } catch (e) {}
  installEvt = null; $("mInstall").hidden = true;
};
addEventListener("offline", () => toast(t("offline")));
if (!navigator.onLine) setTimeout(() => toast(t("offline")), 800);
addEventListener("online", () => toast(t("online")));
if ("serviceWorker" in navigator && (location.protocol === "https:" || location.hostname === "localhost")) {
  addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {}));
}
$("closeDlg").onclick = () => $("dlg").close();
$("grab").onclick = () => setSheet(!sheet.classList.contains("open"));

// ---- GPX route: draw a route and list the water points along it (all client-side)
let route = null, routeMax = 300, routeHits = [];
const ROUTE_STEPS = [150, 300, 600];

function parseGpx(text) {
  const doc = new DOMParser().parseFromString(text, "application/xml");
  if (doc.querySelector("parsererror")) return null;
  let pts = [...doc.getElementsByTagName("trkpt")];
  if (!pts.length) pts = [...doc.getElementsByTagName("rtept")];
  const coords = pts.map(p => [parseFloat(p.getAttribute("lon")), parseFloat(p.getAttribute("lat"))])
    .filter(([lon, lat]) => isFinite(lon) && isFinite(lat) && Math.abs(lat) <= 90 && Math.abs(lon) <= 180);
  return coords.length >= 2 ? coords : null;
}

function buildRoute(full) {
  const cumFull = [0];
  for (let i = 1; i < full.length; i++) cumFull.push(cumFull[i - 1] + haversine(full[i - 1], full[i]));
  const step = Math.max(1, Math.ceil(full.length / 2500)), coords = [], cum = [];
  for (let i = 0; i < full.length; i += step) { coords.push(full[i]); cum.push(cumFull[i]); }
  if ((full.length - 1) % step) { coords.push(full[full.length - 1]); cum.push(cumFull[full.length - 1]); }
  return { coords, cum, total: cumFull[full.length - 1] };
}

function segDist(p, a, b) {
  const k = Math.cos(p[1] * Math.PI / 180), R = 111320;
  const ax = (a[0] - p[0]) * k * R, ay = (a[1] - p[1]) * R, bx = (b[0] - p[0]) * k * R, by = (b[1] - p[1]) * R;
  const dx = bx - ax, dy = by - ay, l2 = dx * dx + dy * dy;
  let u = l2 ? -(ax * dx + ay * dy) / l2 : 0; u = Math.max(0, Math.min(1, u));
  return [Math.hypot(ax + u * dx, ay + u * dy), u];
}

function computeHits() {
  const c = route.coords;
  let w = 180, e = -180, s = 90, n = -90;
  for (const [x, y] of c) { w = Math.min(w, x); e = Math.max(e, x); s = Math.min(s, y); n = Math.max(n, y); }
  const dLat = routeMax * 1.2 / 111320, dLon = dLat / Math.cos(((s + n) / 2) * Math.PI / 180);
  routeHits = [];
  for (const f of data.features) {
    if (!visible(f)) continue;
    const p = f.geometry.coordinates;
    if (p[0] < w - dLon || p[0] > e + dLon || p[1] < s - dLat || p[1] > n + dLat) continue;
    let best = Infinity, along = 0;
    for (let i = 0; i < c.length - 1; i++) {
      const [d, u] = segDist(p, c[i], c[i + 1]);
      if (d < best) { best = d; along = route.cum[i] + u * (route.cum[i + 1] - route.cum[i]); }
    }
    if (best <= routeMax) routeHits.push({ f, d: best, along });
  }
  routeHits.sort((a, b) => a.along - b.along);
  const src = map.getSource("routehits");
  if (src) src.setData({ type: "FeatureCollection", features: routeHits.map(h => h.f) });
}

function renderRouteList(ul) {
  $("sheetTitle").textContent = `${t("routeTitle")} (${routeHits.length})`;
  const marks = [0, ...routeHits.map(h => h.along), route.total];
  let gap = 0; for (let i = 1; i < marks.length; i++) gap = Math.max(gap, marks[i] - marks[i - 1]);
  $("rsum").textContent = t("routeSum")((route.total / 1000).toFixed(1), routeHits.length, (gap / 1000).toFixed(1));
  $("rnote").textContent = t("routeNote");
  const box = $("rbtns"); box.textContent = "";
  for (const m of ROUTE_STEPS) {
    const b = document.createElement("button");
    b.textContent = m + " " + t("m"); b.setAttribute("aria-pressed", m === routeMax);
    b.onclick = () => { routeMax = m; computeHits(); renderList(); };
    box.append(b);
  }
  if (!routeHits.length) { const p = document.createElement("p"); p.className = "empty"; p.textContent = t("routeNone"); ul.append(p); return; }
  for (const { f, d, along } of routeHits) {
    const li = document.createElement("li"), b = document.createElement("button");
    const nm = document.createElement("span"); nm.textContent = labelOf(f.properties);
    const ds = document.createElement("span"); ds.className = "dist";
    ds.textContent = `${(along / 1000).toFixed(1)} ${t("km")} · ${fmtDist(d)}`;
    b.append(dotFor(f.properties), nm, ds); b.onclick = () => { focusOn(f); setSheet(false); };
    li.append(b); ul.append(li);
  }
}

function setRouteOnMap() {
  const line = { type: "Feature", geometry: { type: "LineString", coordinates: route.coords } };
  if (map.getSource("route")) { map.getSource("route").setData(line); return; }
  map.addSource("route", { type: "geojson", data: line });
  map.addSource("routehits", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
  map.addLayer({ id: "route-casing", type: "line", source: "route", layout: { "line-join": "round", "line-cap": "round" }, paint: { "line-color": "#fff", "line-width": 7 } }, "clusters");
  map.addLayer({ id: "route-line", type: "line", source: "route", layout: { "line-join": "round", "line-cap": "round" }, paint: { "line-color": "#ff6b00", "line-width": 4 } }, "clusters");
  map.addLayer({ id: "route-hits", type: "circle", source: "routehits", paint: { "circle-translate": [0, -10], "circle-radius": 14, "circle-color": "rgba(255,107,0,0.18)", "circle-stroke-color": "#ff6b00", "circle-stroke-width": 2.5 } }, "clusters");
}

function loadGpxText(text) {
  const full = parseGpx(text);
  if (!data) { toast(t("stillLoading")); return; }
  if (!full) { toast(t("routeErr")); return; }
  route = buildRoute(full);
  setRouteOnMap(); computeHits(); renderList(); setSheet(true);
  const b = route.coords.reduce((bb, c) => bb.extend(c), new maplibregl.LngLatBounds(route.coords[0], route.coords[0]));
  map.fitBounds(b, { padding: { top: 120, bottom: 240, left: 40, right: 40 }, maxZoom: 16 });
}

function clearRoute() {
  route = null; routeHits = [];
  for (const id of ["route-hits", "route-line", "route-casing"]) if (map.getLayer(id)) map.removeLayer(id);
  for (const id of ["routehits", "route"]) if (map.getSource(id)) map.removeSource(id);
  renderList();
}

const GPX_MAX_BYTES = 25 * 1024 * 1024;
async function handleGpxFile(file) {
  if (!file) return;
  if (file.size > GPX_MAX_BYTES) { toast(t("gpxTooBig")); return; }
  try { loadGpxText(await file.text()); } catch (e) { toast(t("routeErr")); }
}
$("gpxIn").onchange = e => { handleGpxFile(e.target.files[0]); e.target.value = ""; };
$("rclear").onclick = clearRoute;
addEventListener("dragover", e => { e.preventDefault(); document.body.classList.add("drag"); });
addEventListener("dragleave", () => document.body.classList.remove("drag"));
addEventListener("drop", e => { e.preventDefault(); document.body.classList.remove("drag"); handleGpxFile(e.dataTransfer.files[0]); });

// ---- language
function applyLang() {
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-i]").forEach(e => e.textContent = t(e.dataset.i));
  $("pq").placeholder = t("placesSearch");
  $("mAreas").href = lang === "el" ? "vryses/" : "en/areas/";
  $("mTheme").textContent = `${t("theme")}: ${t("theme_" + theme)}`;
  $("lang").textContent = lang === "el" ? "EN" : "ΕΛ";
  $("lang").setAttribute("aria-label", t("langLabel")); $("lang").lang = lang === "el" ? "en" : "el";
  $("menuBtn").setAttribute("aria-label", t("menuLabel"));
  $("map").setAttribute("aria-label", t("mapLabel"));
  if (data) $("updated").textContent = `${t("updated")} OpenStreetMap: ${data.generated || "?"}`;
  try { if (map.getStyle()) setLabelLanguage(); } catch (e) {}   // no-op until the base style has loaded
  renderChips(); renderPlaces(); updateNudge();
  if (data) { renderList(); $("count").textContent = t("points")(data.features.filter(visible).length); }
}
$("lang").onclick = () => { lang = lang === "el" ? "en" : "el"; try { localStorage.setItem("lang", lang); } catch (e) {} applyLang(); };
if (DONATE_URL) { $("donate").hidden = false; $("donateLink").href = DONATE_URL; $("mSupport").hidden = false; $("mSupport").href = DONATE_URL; }
$("stats").hidden = false;
mountDrops();
applyLang();

// ---- keep the base map neutral: no border lines, labels in the app language
function setLabelLanguage() {
  const field = lang === "el" ? ["coalesce", ["get", "name:el"], ["get", "name"]]
                              : ["coalesce", ["get", "name_en"], ["get", "name:latin"], ["get", "name"]];
  for (const l of map.getStyle().layers) {
    if (l.type !== "symbol") continue;
    const tf = map.getLayoutProperty(l.id, "text-field");
    if (tf && JSON.stringify(tf).includes("name")) map.setLayoutProperty(l.id, "text-field", field);
  }
}
function tidyBaseStyle() {
  for (const l of map.getStyle().layers) {
    if (/bound|border|disput|marit/i.test(l.id)) map.setLayoutProperty(l.id, "visibility", "none");
  }
  setLabelLanguage();
}

// ---- base map type (standard / terrain / satellite)
function applyBasemapExtras() {
  const layers = map.getStyle().layers;
  const firstLine = (layers.find(l => l.type === "line" || l.type === "symbol") || {}).id;
  if (basemap === "terrain") {
    map.addSource("dem", { type: "raster-dem", encoding: "terrarium", tileSize: 256, maxzoom: 13,
      tiles: ["https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"],
      attribution: "Terrain: Mapzen / AWS Terrain Tiles (SRTM, USGS and others)" });
    map.addLayer({ id: "hillshade", type: "hillshade", source: "dem", paint: {
      "hillshade-exaggeration": 0.55,
      "hillshade-shadow-color": isDark() ? "#000000" : "#39463c",
      "hillshade-highlight-color": isDark() ? "#5c6b78" : "#ffffff",
      "hillshade-accent-color": isDark() ? "#2a3642" : "#6b7c6f" } }, firstLine);
  } else if (basemap === "satellite") {
    for (const l of layers) if (["fill", "background", "fill-extrusion"].includes(l.type)) map.setLayoutProperty(l.id, "visibility", "none");
    map.addSource("sat", { type: "raster", tileSize: 256, maxzoom: 13,
      tiles: ["https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/{z}/{y}/{x}.jpg"],
      attribution: "Sentinel-2 cloudless by EOX IT Services GmbH (Contains modified Copernicus Sentinel data 2016)" });
    map.addLayer({ id: "sat", type: "raster", source: "sat" }, firstLine);
  }
}
function reloadStyle() { map.setStyle(styleUrl(), { diff: false }); }   // full reload, so "style.load" fires and redraws everything
function setBasemap(name) {
  if (name === basemap) return;
  basemap = name;
  try { localStorage.setItem("basemap", name); } catch (e) {}
  reloadStyle();
}
document.querySelectorAll('input[name="bm"]').forEach(r => r.onchange = () => { setBasemap(r.value); $("bdlg").close(); });
$("bClose").onclick = () => $("bdlg").close();

// ---- data layers (re-added every time the base style loads)
function dropImage(grade) {
  const W = 48, H = 60, c = document.createElement("canvas"); c.width = W; c.height = H;
  const ctx = c.getContext("2d"), solid = grade !== "other";
  ctx.scale(W / 24, H / 30);
  const path = new Path2D(DROP_PATH);
  ctx.fillStyle = solid ? DROP_BLUE : "#ffffff"; ctx.fill(path);
  ctx.lineWidth = solid ? 1.6 : 3; ctx.strokeStyle = solid ? "#ffffff" : RING; ctx.lineJoin = "round"; ctx.stroke(path);
  return ctx.getImageData(0, 0, W, H);
}
function addDropImages() { for (const g of ["drink", "other"]) if (!map.hasImage("drop-" + g)) map.addImage("drop-" + g, dropImage(g), { pixelRatio: 2 }); }

function installData() {
  if (map.getSource("water")) return;
  map.addSource("water", { type: "geojson", data, cluster: true, clusterRadius: 44, clusterMaxZoom: 14 });
  map.addLayer({ id: "clusters", type: "circle", source: "water", filter: ["has", "point_count"],
    paint: { "circle-color": DROP_BLUE, "circle-opacity": .9, "circle-stroke-color": "#fff", "circle-stroke-width": 2,
             "circle-radius": ["step", ["coalesce", ["get", "point_count"], 0], 15, 25, 19, 100, 24, 400, 30] } });
  map.addLayer({ id: "cluster-count", type: "symbol", source: "water", filter: ["has", "point_count"],
    layout: { "text-field": ["get", "point_count_abbreviated"], "text-font": ["Noto Sans Bold"], "text-size": 13 },
    paint: { "text-color": "#fff" } });
  addDropImages();
  map.addLayer({ id: "points", type: "symbol", source: "water", filter: ["!", ["has", "point_count"]],
    layout: { "icon-image": ["match", ["get", "grade"], "other", "drop-other", "drop-drink"], "icon-anchor": "bottom",
              "icon-allow-overlap": true, "icon-ignore-placement": true,
              "icon-size": ["interpolate", ["linear"], ["zoom"], 8, 0.55, 16, 1] } });
}
map.on("click", "clusters", e => {
  const f = e.features[0];
  map.getSource("water").getClusterExpansionZoom(f.properties.cluster_id).then(z => map.easeTo({ center: f.geometry.coordinates, zoom: z + .5 }));
});
map.on("click", "points", e => focusOn(e.features[0]));
for (const l of ["clusters", "points"]) {
  map.on("mouseenter", l, () => map.getCanvas().style.cursor = "pointer");
  map.on("mouseleave", l, () => map.getCanvas().style.cursor = "");
}

// ---- data: fetched in parallel with the base map and drawn as soon as the style is ready
const dataReady = fetch("water.geojson")
  .then(r => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
  .then(d => {
    if (!d || !Array.isArray(d.features)) throw new Error("bad data");
    d.features = d.features.filter(f => f && f.properties && f.geometry && Array.isArray(f.geometry.coordinates)
      && isFinite(f.geometry.coordinates[0]) && isFinite(f.geometry.coordinates[1]));
    return d;
  });
dataReady.catch(() => {});                              // reported in the style.load handler
let firstStyle = true, styleGen = 0;
map.on("style.load", async () => {
  const gen = ++styleGen;
  try { data = data || await dataReady; }
  catch (e) {
    $("count").textContent = "⚠";
    toast(t("dataFail"));
    const b = document.createElement("button"); b.className = "locbtn"; b.textContent = t("retry");
    b.onclick = () => location.reload();
    $("list").replaceChildren(b); setSheet(true);
    return;
  }
  if (gen !== styleGen) return;                          // the theme or map type changed while we waited
  if (firstStyle) { for (const f of data.features) f.properties.grade = gradeOf(f.properties); countPlaces(); }
  tidyBaseStyle();
  applyBasemapExtras();
  installData();
  if (route) { setRouteOnMap(); computeHits(); }
  applyFilter();
  if (firstStyle) {
    applyLang();
    // If location permission was already granted and this isn't a shared link, centre on the user right away.
    if (!startedWithHash && navigator.permissions) {
      navigator.permissions.query({ name: "geolocation" }).then(r => { if (r.state === "granted") geolocate.trigger(); }).catch(() => {});
    }
  }
  firstStyle = false;
});
