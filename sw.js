"use strict";
/* Service worker for Νεράκι.
   Rule of thumb: anything that changes (the page, the weekly water data) is fetched from the network first and only
   falls back to the saved copy when offline. Only things that never change (icons, the pinned map library) are
   served from the cache first. Bump VERSION to throw away every saved copy on the next visit. */
const VERSION = "v1";
const SHELL = `shell-${VERSION}`, DATA = `data-${VERSION}`, LIBS = `libs-${VERSION}`, TILES = `tiles-${VERSION}`;
const KEEP = new Set([SHELL, DATA, LIBS, TILES]);
const MAX_TILES = 700;
const PRECACHE = ["./", "./manifest.webmanifest", "./icons/icon-192.png", "./icons/icon-512.png", "./water.geojson"];

self.addEventListener("install", e => {
  e.waitUntil((async () => {
    const shell = await caches.open(SHELL), data = await caches.open(DATA);
    await Promise.allSettled(PRECACHE.map(u => (u.endsWith("water.geojson") ? data : shell).add(new Request(u, { cache: "reload" }))));
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (!KEEP.has(k)) await caches.delete(k);
    await self.clients.claim();
  })());
});

const okToStore = r => r && (r.ok || r.type === "opaque");

async function networkFirst(req, cacheName, ms = 6000) {
  const cache = await caches.open(cacheName);
  try {
    const ctl = new AbortController(), timer = setTimeout(() => ctl.abort(), ms);
    const res = await fetch(req, { cache: "no-cache", signal: ctl.signal });
    clearTimeout(timer);
    if (okToStore(res)) cache.put(req, res.clone());
    return res;
  } catch (err) {
    const hit = await cache.match(req, { ignoreSearch: true });
    if (hit) return hit;
    throw err;
  }
}

async function staleWhileRevalidate(req, cacheName) {
  const cache = await caches.open(cacheName);
  const hit = await cache.match(req);
  const net = fetch(req).then(res => { if (okToStore(res)) cache.put(req, res.clone()); return res; }).catch(() => null);
  return hit || (await net) || Response.error();
}

async function cacheFirst(req, cacheName, trimTo) {
  const cache = await caches.open(cacheName);
  const hit = await cache.match(req);
  if (hit) return hit;
  const res = await fetch(req);
  if (okToStore(res)) {
    await cache.put(req, res.clone());
    if (trimTo) trim(cache, trimTo);
  }
  return res;
}

async function trim(cache, max) {
  const keys = await cache.keys();
  for (let i = 0; i < keys.length - max; i++) await cache.delete(keys[i]);   // oldest first
}

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  if (url.origin === self.location.origin) {
    if (url.pathname.endsWith("/sw.js")) return;                                   // always let the browser check for a new worker
    if (url.pathname.endsWith("water.geojson")) return void e.respondWith(networkFirst(req, DATA));
    const isPage = req.mode === "navigate" || req.destination === "document" || url.pathname.endsWith("/") || url.pathname.endsWith(".html");
    if (isPage) return void e.respondWith(networkFirst(req, SHELL));
    return void e.respondWith(staleWhileRevalidate(req, SHELL));                   // icons, manifest
  }
  if (url.hostname === "cdn.jsdelivr.net" && url.pathname.includes("maplibre-gl@")) {
    return void e.respondWith(cacheFirst(req, LIBS));                              // pinned version: never changes
  }
  if (url.hostname === "tiles.openfreemap.org") {
    if (url.pathname.startsWith("/styles/")) return void e.respondWith(staleWhileRevalidate(req, TILES));
    return void e.respondWith(cacheFirst(req, TILES, MAX_TILES));                  // tiles, sprites, fonts
  }
  // Everything else (analytics, Ko-fi, other tile sources) goes straight to the network.
});
