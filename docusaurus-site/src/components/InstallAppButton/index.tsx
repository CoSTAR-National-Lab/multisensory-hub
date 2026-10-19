import React, { useEffect, useId, useRef, useState } from 'react';
import { INSTALL_PROMPT_EVENT } from '@site/src/pwa/installPrompt';
import styles from './styles.module.css';

/*
 * Navbar icon, next to search, offering to install the site as an app for
 * offline reading (rendered by src/theme/Navbar/Content). No pop-ups: it
 * renders nothing until the browser can actually install the site, and the
 * offline copy is only downloaded once the site is installed
 * (plugin-pwa offlineModeActivationStrategies).
 *
 * - Chromium (Chrome, Edge, Android): shows the deferred native install
 *   prompt captured by src/pwa/installPrompt.js.
 * - iOS / macOS Safari: no programmatic prompt exists, so a small panel under
 *   the icon explains how to add it.
 * - Firefox desktop, or already installed: nothing is shown.
 * - Running as the installed app: the icon shows whether the offline copy is
 *   saved.
 */

type Mode = 'none' | 'prompt' | 'ios' | 'mac-safari' | 'standalone';

type OfflineStatus = 'saving' | 'saved';

const INSTALL_LABEL = 'Install as an app for offline reading';

function isStandalone(): boolean {
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    (navigator as Navigator & { standalone?: boolean }).standalone === true
  );
}

function isIOS(): boolean {
  return (
    /iphone|ipad|ipod/i.test(navigator.userAgent) ||
    (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
  );
}

function isMacSafari(): boolean {
  const ua = navigator.userAgent;
  return (
    /Macintosh/.test(ua) &&
    /Safari/.test(ua) &&
    !/Chrome|Chromium|Edg|OPR|Firefox/.test(ua)
  );
}

// plugin-pwa encodes {offlineMode, debug} in the service worker URL.
function isOfflineWorker(worker: ServiceWorker | null): boolean {
  if (!worker) {
    return false;
  }
  try {
    const params = new URL(worker.scriptURL).searchParams.get('params');
    return !!params && JSON.parse(params).offlineMode === true;
  } catch {
    return false;
  }
}

async function getOfflineStatus(): Promise<OfflineStatus> {
  const reg = await navigator.serviceWorker?.getRegistration();
  // A worker reaches "waiting" or "active" only after its precache finished.
  return reg && (isOfflineWorker(reg.active) || isOfflineWorker(reg.waiting))
    ? 'saved'
    : 'saving';
}

function getPrompt(): any {
  return (window as any).__mshubInstallPrompt ?? null;
}

function DownloadIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 3v12M7 10l5 5 5-5M4 20h16" />
    </svg>
  );
}

function SavedIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M7 18a4.5 4.5 0 0 1-.5-8.97A6 6 0 0 1 18 9.5a4 4 0 0 1-.5 8.5H7Z" />
      <path d="m9.5 13.5 2 2 3.5-3.5" />
    </svg>
  );
}

function SavingIcon() {
  return (
    <svg className={styles.spin} width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
      <path d="M21 12a9 9 0 1 1-6.2-8.56" />
    </svg>
  );
}

export default function InstallAppButton() {
  const [mode, setMode] = useState<Mode>('none');
  const [open, setOpen] = useState(false);
  const [offlineStatus, setOfflineStatus] = useState<OfflineStatus>('saving');
  const panelId = useId();
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const update = () => {
      if (isStandalone()) {
        setMode('standalone');
      } else if (getPrompt()) {
        setMode('prompt');
      } else if (isIOS()) {
        setMode('ios');
      } else if (isMacSafari()) {
        setMode('mac-safari');
      } else {
        setMode('none');
      }
    };
    update();
    window.addEventListener(INSTALL_PROMPT_EVENT, update);
    return () => window.removeEventListener(INSTALL_PROMPT_EVENT, update);
  }, []);

  // In the installed app, poll until the offline copy is saved.
  useEffect(() => {
    if (mode !== 'standalone') {
      return undefined;
    }
    let timer: number | undefined;
    const check = async () => {
      const status = await getOfflineStatus();
      setOfflineStatus(status);
      if (status === 'saving') {
        timer = window.setTimeout(check, 2000);
      }
    };
    void check();
    return () => window.clearTimeout(timer);
  }, [mode]);

  // Close the panel on outside click or Escape.
  useEffect(() => {
    if (!open) {
      return undefined;
    }
    const onMouseDown = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', onMouseDown);
    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.removeEventListener('mousedown', onMouseDown);
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [open]);

  if (mode === 'none') {
    return null;
  }

  const onClick = async () => {
    if (mode === 'prompt') {
      const prompt = getPrompt();
      if (!prompt) {
        return;
      }
      prompt.prompt();
      await prompt.userChoice;
      // A deferred prompt can only be used once; the icon goes until the
      // browser offers another one.
      (window as any).__mshubInstallPrompt = null;
      setMode('none');
      return;
    }
    setOpen((value) => !value);
  };

  let label = INSTALL_LABEL;
  let icon = <DownloadIcon />;
  let panelText = '';
  if (mode === 'standalone') {
    label =
      offlineStatus === 'saved'
        ? 'Saved for offline reading'
        : 'Saving for offline reading…';
    icon = offlineStatus === 'saved' ? <SavedIcon /> : <SavingIcon />;
    panelText =
      offlineStatus === 'saved'
        ? 'The whole hub, including search, is saved on this device and works without an internet connection.'
        : 'The hub is being saved to this device so it works without an internet connection. Keep the app open until this finishes.';
  } else if (mode === 'ios') {
    panelText =
      'Tap the Share button, then “Add to Home Screen”. Open the hub from your home screen once while online and it will be saved for offline reading.';
  } else if (mode === 'mac-safari') {
    panelText =
      'In Safari, choose File › Add to Dock. Open the hub from the Dock once while online and it will be saved for offline reading.';
  }
  const hasPanel = mode !== 'prompt';

  return (
    <div className={styles.root} ref={rootRef}>
      <button
        type="button"
        className={styles.trigger}
        onClick={onClick}
        aria-label={label}
        title={label}
        aria-expanded={hasPanel ? open : undefined}
        aria-controls={hasPanel ? panelId : undefined}
      >
        {icon}
      </button>
      {hasPanel && open && (
        <div id={panelId} className={styles.panel} role="dialog" aria-label={label}>
          <p className={styles.panelTitle}>{label}</p>
          <p className={styles.panelText}>{panelText}</p>
        </div>
      )}
    </div>
  );
}
