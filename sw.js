const CACHE_NAME = 'camara-match-v2'; // Le subimos la versión para forzar la actualización
const urlsToCache = [
  '/movie-match/',
  '/movie-match/index.html',
  '/movie-match/resultados.html'
  // OJO: Quitamos el peliculas.json de la lista de caché
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  // NUEVO: Si el archivo es el JSON de películas, lo buscamos SIEMPRE en la red
  if (event.request.url.includes('peliculas.json')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // Para el resto de los archivos, usamos la caché normal
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
