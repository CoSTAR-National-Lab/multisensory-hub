/*
 * Runs inside the service worker built by @docusaurus/plugin-pwa (swCustom).
 *
 * With trailingSlash: false, pages are built as /about-page.html and served at
 * /about-page. The plugin's offline lookup only tries /about-page and
 * /about-page/index.html, so reloading or cold-launching a subpage offline
 * would fail. This listener is added before the plugin's, and answers
 * extension-less navigations from the precached .html file. Precache keys
 * carry a __WB_REVISION__ query, hence ignoreSearch.
 */
export default function swCustom(params) {
  if (!params.offlineMode) {
    return;
  }
  self.addEventListener('fetch', (event) => {
    const {request} = event;
    if (request.mode !== 'navigate') {
      return;
    }
    const url = new URL(request.url);
    if (
      url.origin !== self.location.origin ||
      url.pathname.endsWith('/') ||
      /\.[a-z0-9]+$/i.test(url.pathname)
    ) {
      return;
    }
    event.respondWith(
      caches
        .match(`${url.pathname}.html`, {ignoreSearch: true})
        .then((cached) => cached || fetch(request)),
    );
  });
}
