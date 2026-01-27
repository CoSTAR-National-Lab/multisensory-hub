import React, { useState, useEffect } from 'react';
import styles from './styles.module.css';

const STORAGE_KEY = 'dyslexia-font-enabled';

export default function DyslexiaToggle(): JSX.Element {
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    // Load preference from localStorage on mount
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === 'true') {
      setEnabled(true);
      document.documentElement.setAttribute('data-dyslexia-font', 'true');
    }
  }, []);

  const toggleDyslexiaFont = () => {
    const newValue = !enabled;
    setEnabled(newValue);

    if (newValue) {
      document.documentElement.setAttribute('data-dyslexia-font', 'true');
      localStorage.setItem(STORAGE_KEY, 'true');
    } else {
      document.documentElement.removeAttribute('data-dyslexia-font');
      localStorage.setItem(STORAGE_KEY, 'false');
    }
  };

  return (
    <button
      className={`${styles.toggle} ${enabled ? styles.enabled : ''}`}
      onClick={toggleDyslexiaFont}
      title={enabled ? 'Disable dyslexia-friendly font' : 'Enable dyslexia-friendly font'}
      aria-pressed={enabled}
      aria-label="Toggle dyslexia-friendly font"
    >
      <span className={styles.icon}>Aa</span>
      <span className={styles.label}>Dyslexia Font</span>
    </button>
  );
}
