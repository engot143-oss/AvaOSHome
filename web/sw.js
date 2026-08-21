// Service Worker for AVA OS PWA
const CACHE_NAME = 'ava-v1';
const ASSETS = [
    '/',
    '/index.html',
    '/manifest.json',
    '/sw.js'
];

// Install event
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(ASSETS);
        })
    );
    self.skipWaiting();
});

// Activate event
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
        })
    );
    self.clients.claim();
});

// Fetch event - Network first, then cache
self.addEventListener('fetch', event => {
    event.respondWith(
        fetch(event.request)
            .then(response => {
                // Cache successful responses
                if (response.ok) {
                    const cache = caches.open(CACHE_NAME);
                    cache.then(c => c.put(event.request, response.clone()));
                }
                return response;
            })
            .catch(() => {
                // Fall back to cache if network fails
                return caches.match(event.request)
                    .then(response => response || new Response('Offline', { status: 503 }));
            })
    );
});
