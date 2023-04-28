const CACHE_NAME = 'chat-app-cache-v1';
const urlsToCache = [];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  if (event.request.url.startsWith('http')) {
    const url = event.request.url;
    if (url.includes('/backend-api/') || url.endsWith('/chat') || url.endsWith('/chat#')) {
      return;
    }
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }

        return fetch(event.request)
          .then(response => {
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            const responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then(cache => cache.put(event.request, responseToCache));

            return response;
          });
      })
  );
  }
});
