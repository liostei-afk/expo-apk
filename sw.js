// Service worker: cachea la app para que funcione sin conexión una vez instalada.
// Subí CACHE_VERSION cada vez que cambies feria-china-tracker.html para forzar la actualización.
const CACHE_VERSION = 'feria-china-v3';
const APP_SHELL = [
  './feria-china-tracker.html',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then(cache => cache.addAll(APP_SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE_VERSION).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const req = event.request;
  // Solo cachea lo propio de la app.
  if (req.method !== 'GET' || !req.url.startsWith(self.location.origin)) return;

  // Para el HTML de la app: red primero (así una versión nueva se ve enseguida,
  // sin tener que abrir la app dos veces), con el caché como respaldo offline.
  const isDocument = req.mode === 'navigate' || req.destination === 'document';
  if (isDocument) {
    event.respondWith(
      fetch(req)
        .then(res => {
          if (res.ok) {
            const copy = res.clone();
            caches.open(CACHE_VERSION).then(c => c.put(req, copy));
          }
          return res;
        })
        .catch(() => caches.match(req).then(cached => cached || caches.match('./feria-china-tracker.html')))
    );
    return;
  }

  // Para el resto (íconos, manifest): caché primero, refrescando en segundo plano.
  event.respondWith(
    caches.match(req).then(cached => {
      const network = fetch(req)
        .then(res => {
          if (res.ok) {
            const copy = res.clone();
            caches.open(CACHE_VERSION).then(c => c.put(req, copy));
          }
          return res;
        })
        .catch(() => cached);
      return cached || network;
    })
  );
});
