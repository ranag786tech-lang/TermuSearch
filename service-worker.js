const CACHE_NAME = "digid-search-v1";
const urlsToCache = ["/", "/index.html", "/style.css", "/script.js", "/data.js"];

self.addEventListener("install", event => {
    event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache)));
});

self.addEventListener("fetch", event => {
    event.respondWith(caches.match(event.request).then(response => response || fetch(event.request)));
});
