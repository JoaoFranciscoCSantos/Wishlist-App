const CACHE_NAME = "wishlist-cache-v1";

// Só cacheamos ficheiros estáticos (CSS, ícones, manifest).
// As páginas (/, /add, /edit/...) mostram dados da base de dados
// que mudam constantemente, por isso não as metemos em cache:
// tentamos sempre a rede primeiro para elas.
const ESTATICOS = [
  "/static/style.css",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png",
  "/manifest.json",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ESTATICOS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((nomes) =>
      Promise.all(
        nomes
          .filter((nome) => nome !== CACHE_NAME)
          .map((nome) => caches.delete(nome))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const { request } = event;

  // Páginas dinâmicas (navegação): rede primeiro, cache só como fallback
  // se estiveres offline (mostra a última versão vista da página).
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request).catch(() => caches.match(request))
    );
    return;
  }

  // Ficheiros estáticos: cache primeiro, rede como reserva.
  if (ESTATICOS.some((path) => request.url.endsWith(path))) {
    event.respondWith(
      caches.match(request).then((cached) => cached || fetch(request))
    );
  }
});
