import React, { useState, useEffect } from 'react';
import styles from './index.module.css';

const OPTOUT_KEY = 'concept_analytics_optout';

function readOptOut() {
  try { return localStorage.getItem(OPTOUT_KEY) === '1'; } catch { return false; }
}

export default function Footer() {
  // Initialise as false; real value set client-side in useEffect (SSR safety).
  const [optedOut, setOptedOut] = useState(false);
  const [justConfirmed, setJustConfirmed] = useState(false);

  useEffect(() => {
    // Honour Global Privacy Control automatically.
    if (navigator.globalPrivacyControl === true) {
      try { localStorage.setItem(OPTOUT_KEY, '1'); } catch {}
    }
    setOptedOut(readOptOut());
  }, []);

  function handleOptOut() {
    try { localStorage.setItem(OPTOUT_KEY, '1'); } catch {}
    setOptedOut(true);
    setJustConfirmed(true);
    setTimeout(() => setJustConfirmed(false), 4000);
  }

  function handleOptIn() {
    try { localStorage.removeItem(OPTOUT_KEY); } catch {}
    setOptedOut(false);
  }

  return (
    <footer className={styles.footer}>
      <div className={styles.inner}>
        <p className={styles.notice}>
          We collect anonymous, aggregate engagement data to understand which
          topics and sections of this report are useful to visitors. We do not
          collect names, emails, raw IP addresses, or use third-party advertising
          analytics.
        </p>
        <div className={styles.controls}>
          {optedOut ? (
            <>
              <span className={styles.status}>Analytics opt-out is active.</span>
              <button className={styles.btn} onClick={handleOptIn}>
                Opt back in
              </button>
            </>
          ) : (
            <>
              <button className={styles.btn} onClick={handleOptOut}>
                Opt out of analytics
              </button>
              {justConfirmed && (
                <span className={styles.confirmed}>Opted out.</span>
              )}
            </>
          )}
        </div>
        <div className={styles.copyright}>Multisensory Hub</div>
      </div>
    </footer>
  );
}
