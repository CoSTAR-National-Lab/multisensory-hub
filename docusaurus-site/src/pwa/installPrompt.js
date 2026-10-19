/*
 * Client module: catches Chromium's beforeinstallprompt before React mounts,
 * so the browser's own install banner/mini-infobar is suppressed and the
 * navbar InstallAppButton can show the prompt on demand instead.
 */
import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';

export const INSTALL_PROMPT_EVENT = 'mshub:installprompt';

if (ExecutionEnvironment.canUseDOM) {
  window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault();
    window.__mshubInstallPrompt = event;
    window.dispatchEvent(new Event(INSTALL_PROMPT_EVENT));
  });
  window.addEventListener('appinstalled', () => {
    window.__mshubInstallPrompt = null;
    window.dispatchEvent(new Event(INSTALL_PROMPT_EVENT));
  });
}
