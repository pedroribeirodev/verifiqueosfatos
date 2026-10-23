const CACHE_NAME = 'pwa-static-v8'; // Incremented cache version
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './normalize.css',
  './style.css',
  './manifest.json',
  './lula.webp',
  './flavio.webp',
  './favicon.ico',
  './apple-touch-icon.png',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png'
];

// 1. Install Event: Cache essential app shell files
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Caching app shell');
        return cache.addAll(ASSETS_TO_CACHE);
      })
      .then(() => self.skipWaiting())
  );
});

// 2. Activate Event: Clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keyList) => {
      return Promise.all(
        keyList.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('[Service Worker] Removing old cache', key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// 3. Fetch Event: Exclude /posts.json from cache
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Check if the request path ends with /posts.json or matches posts.json
  if (url.pathname.endsWith('/posts.json')) {
    // Network-Only strategy: bypass cache completely
    event.respondWith(fetch(event.request));
    return;
  }

  // Cache-First strategy for all other static assets
  event.respondWith(
    caches.match(event.request)
      .then((cachedResponse) => {
        return cachedResponse || fetch(event.request);
      })
  );
});