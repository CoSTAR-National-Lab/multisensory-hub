/*
 * Swizzled from @docusaurus/plugin-pwa: no "New version available" pop-up.
 * The new service worker waits, and takes over the next time the installed
 * app is opened (once every window of the old version has closed).
 */
export default function PwaReloadPopup() {
  return null;
}
