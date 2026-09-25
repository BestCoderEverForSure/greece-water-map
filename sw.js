"use strict";
/* Service worker for Νεράκι.
   Rule of thumb: anything that changes (the pages, the app code, the weekly water data) is fetched from the network
   first and only falls back to the saved copy when offline or very slow. Only things that never change (icons, the
   pinned map library, map tiles) are served from the cache first. Bump VERSION to throw away every saved copy on the
   next visit. Saving to the cache is best effort: a full disk must never break a request that the network answered. */
const VERSION = "v2";
const SHELL = `shell-${VERSION}`, DATA = `data-${VERSION}`, LIBS = `libs-${VERSION}`, TILES = `tiles-${VERSION}`;
const KEEP = new Set([SHELL, DATA, LIBS, TILES]);
const MAX_TILES = 700;
const SLOW_MS = 6000;         // after this long without a network answer, use the saved copy if there is one
const LIB = "./vendor/maplibre-gl-4.7.1/";
const PRECACHE = ["./", "./app.js", "./app.css", "./manifest.webmanifest", "./icons/icon-192.png", "./icons/icon-512.png", "./water.geojson",
                  LIB + "maplibre-gl.js", LIB + "maplibre-gl.css"];
const TILE_HOSTS = new Set(["tiles.openfreemap.org", "s3.amazonaws.com", "tiles.maps.eox.at"]);

self.addEventListener("install", e => {
  e.waitUntil((async () => {
    const shell = await caches.open(SHELL), data = await caches.open(DATA), libs = await caches.open(LIBS);
    const target = u => u.endsWith("water.geojson") ? data : u.includes("/vendor/") ? libs : shell;
    await Promise.allSettled(PRECACHE.map(u => target(u).add(new Request(u, { cache: "reload" }))));
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (!KEEP.has(k)) await caches.delete(k);
    await self.clients.claim();
  })());
});

// Opaque responses are never stored: Chrome counts each one as several MB of quota.
const okToStore = r => r && r.ok && r.type !== "opaque";

async function safePut(cache, req, res) {
  try { await cache.put(req, res); } catch (e) { /* quota full or cache unavailable: serving still works */ }
}

async function networkFirst(req, cacheName, fallback) {
  const cache = await caches.open(cacheName);
  const network = fetch(req, { cache: "no-cache" }).then(res => {
    if (okToStore(res)) safePut(cache, req, res.clone());
    return res;
  });
  network.catch(() => {});                                     // handled below; avoid an unhandled rejection
  const saved = () => cache.match(req, { ignoreSearch: true });
  const slow = new Promise(resolve => setTimeout(resolve, SLOW_MS, "slow"));
  const first = await Promise.race([network.then(r => r, () => "failed"), slow]);
  if (first !== "slow" && first !== "failed") return first;
  const hit = await saved();
  if (hit) return hit;                                         // offline or slow, and we have a copy
  if (first === "slow") {                                      // slow, no copy: keep waiting for the network
    try { return await network; } catch (e) { /* fall through */ }
  }
  if (fallback) return fallback();
  return Response.error();
}

async function staleWhileRevalidate(req, cacheName) {
  const cache = await caches.open(cacheName);
  const hit = await cache.match(req);
  const net = fetch(req).then(res => { if (okToStore(res)) safePut(cache, req, res.clone()); return res; }).catch(() => null);
  return hit || (await net) || Response.error();
}

async function cacheFirst(req, cacheName, trimTo) {
  const cache = await caches.open(cacheName);
  const hit = await cache.match(req);
  if (hit) return hit;
  const res = await fetch(req);
  if (okToStore(res)) {
    safePut(cache, req, res.clone()).then(() => { if (trimTo) trim(cache, trimTo); });
  }
  return res;
}

async function trim(cache, max) {
  try {
    const keys = await cache.keys();
    for (let i = 0; i < keys.length - max; i++) await cache.delete(keys[i]);   // oldest first
  } catch (e) { /* ignore */ }
}

function offlinePage(url) {
  const en = url.pathname.includes("/en/") || url.searchParams.get("lang") === "en";
  const home = new URL(self.registration.scope).pathname + (en ? "?lang=en" : "");
  const [title, body, link] = en
    ? ["You're offline", "This page hasn't been saved on this device yet. The map still works offline with the points already saved.", "Open the map"]
    : ["Χωρίς σύνδεση", "Αυτή η σελίδα δεν έχει αποθηκευτεί ακόμα σε αυτή τη συσκευή. Ο χάρτης λειτουργεί και χωρίς σύνδεση με τα σημεία που έχουν ήδη αποθηκευτεί.", "Άνοιγμα του χάρτη"];
  const html = `<!doctype html><html lang="${en ? "en" : "el"}"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title><style>body{font:16px/1.5 system-ui,sans-serif;max-width:32rem;margin:15vh auto;padding:0 16px;color:#14232b;background:#f6f4ef}
@media(prefers-color-scheme:dark){body{color:#e8eef3;background:#0f1a24}a{color:#7cc0ee}}a{color:#0d5eaf;font-weight:600}</style>
<h1>${title}</h1><p>${body}</p><p><a href="${home}">${link}</a></p></html>`;
  return new Response(html, { status: 503, headers: { "Content-Type": "text/html; charset=utf-8" } });
}

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  if (url.origin === self.location.origin) {
    if (url.pathname.endsWith("/sw.js")) return;                                   // always let the browser check for a new worker
    if (url.pathname.endsWith("water.geojson")) return void e.respondWith(networkFirst(req, DATA));
    if (req.mode === "navigate") return void e.respondWith(networkFirst(req, SHELL, () => offlinePage(url)));
    if (url.pathname.includes("/vendor/")) return void e.respondWith(cacheFirst(req, LIBS));   // versioned paths: never change
    if (/\.(html|js|css|webmanifest)$/.test(url.pathname) || url.pathname.endsWith("/")) {
      return void e.respondWith(networkFirst(req, SHELL));                         // app code: must match the page
    }
    return void e.respondWith(staleWhileRevalidate(req, SHELL));                   // icons
  }
  if (TILE_HOSTS.has(url.hostname)) {
    if (url.hostname === "s3.amazonaws.com" && !url.pathname.startsWith("/elevation-tiles-prod/")) return;
    if (url.pathname.startsWith("/styles/")) return void e.respondWith(staleWhileRevalidate(req, TILES));
    return void e.respondWith(cacheFirst(req, TILES, MAX_TILES));                  // tiles, sprites, fonts, terrain, satellite
  }
  // Everything else (analytics, Ko-fi, links to other sites) goes straight to the network.
});
