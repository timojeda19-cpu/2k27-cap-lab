const CACHE_NAME = 'nba2k27-lab-2k27-s2-v1';
const ASSETS = ["./", "./index.html", "./manifest.json", "./icon.svg", "./icon-512.png", "./icon-192.png", "./apple-touch-icon.png"];
self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then((cached) => cached || fetch(e.request).then((r) => {
      if (r && r.status === 200 && r.type === 'basic') {
        const copy = r.clone(); caches.open(CACHE_NAME).then((c) => c.put(e.request, copy));
      }
      return r;
    }).catch(() => caches.match('./index.html')))
  );
});
