const CACHE_NAME = "coffeetrader-cache-v1";
const urlsToCache = [
    "/",
    "/dashboard",
    "/lots_commandes",
    "/static/style.css",
    "/static/icons/icon-192x192.png",
    "/static/icons/icon-512x512.png"
];

// Installation du service worker
self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

// Interception des requêtes pour servir les fichiers mis en cache
self.addEventListener("fetch", event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
});
