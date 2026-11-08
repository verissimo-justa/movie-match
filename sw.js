const CACHE_NAME = 'camara-match-v3'; // Subimos la versión para forzar la actualización
const urlsToCache = [
  '/movie-match/',
  '/movie-match/index.html'
];

// Instalamos el nuevo Service Worker y forzamos que tome el control de inmediato
self.addEventListener('install', event => {
  self.skipWaiting(); 
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

// Cuando se activa, borramos las cachés viejas
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim()) // Toma el control de las pestañas abiertas
  );
});

self.addEventListener('fetch', event => {
  // Estrategia: Network First (Red primero, caché como respaldo)
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Si la respuesta es buena, la guardamos en caché por si acaso
        if (response && response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        // Si falla la red (sin internet), buscamos en la caché
        return caches.match(event.request);
      })
  );
});
