const CACHE_NAME = 'camara-match-v1';
const urlsToCache = [
  '/movie-match/',
  '/movie-match/index.html',
  '/movie-match/peliculas.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
