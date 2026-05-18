import React, { useState, useEffect } from 'react';
import styles from './index.module.css';

const OPTOUT_KEY = 'concept_analytics_optout';

function readOptOut() {
  try { return localStorage.getItem(OPTOUT_KEY) === '1'; } catch { return false; }
}

export default function Footer() {
  const [optedOut, setOptedOut] = useState(false);
  const [justConfirmed, setJustConfirmed] = useState(false);

  useEffect(() => { setOptedOut(readOptOut()); }, []);

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
        <span className={styles.notice}>
          Anonymous engagement data is collected to understand which sections are most useful.
          No personal data is stored. Part of the{' '}
          <a href="https://www.costarnetwork.co.uk" target="_blank" rel="noopener noreferrer" className={styles.link}>CoSTAR Network</a>.
        </span>
        <span className={styles.sep}>·</span>
        <a href="https://www.costarnetwork.co.uk/cookie-policy-for-costar-network-website" target="_blank" rel="noopener noreferrer" className={styles.link}>Cookies</a>
        <span className={styles.sep}>·</span>
        <a href="https://www.costarnetwork.co.uk/costar-national-lab-privacy-policy" target="_blank" rel="noopener noreferrer" className={styles.link}>Privacy</a>
        <span className={styles.sep}>·</span>
        {optedOut ? (
          <>
            <span className={styles.status}>Analytics off.</span>
            <button className={styles.btn} onClick={handleOptIn}>Opt in</button>
          </>
        ) : (
          <>
            <button className={styles.btn} onClick={handleOptOut}>Opt out</button>
            {justConfirmed && <span className={styles.confirmed}>Opted out.</span>}
          </>
        )}
      </div>
    </footer>
  );
}
