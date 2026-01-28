import React, { useState, useEffect, useRef } from 'react';
import styles from './styles.module.css';

const STORAGE_KEY_FONT = 'reading-settings-font';
const STORAGE_KEY_WORD_SPACING = 'reading-settings-word-spacing';
const STORAGE_KEY_LINE_SPACING = 'reading-settings-line-spacing';
const OLD_DYSLEXIA_KEY = 'dyslexia-font-enabled';

type FontOption = 'default' | 'lexend' | 'system';
type WordSpacingOption = 'wide' | 'normal' | 'narrow';
type LineSpacingOption = 'relaxed' | 'normal' | 'compact';

interface ReadingSettingsProps {
  /** If true, renders as a panel instead of dropdown (for mobile sidebar) */
  variant?: 'dropdown' | 'panel';
}

export default function ReadingSettings({ variant = 'dropdown' }: ReadingSettingsProps): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);
  const [font, setFont] = useState<FontOption>('default');
  const [wordSpacing, setWordSpacing] = useState<WordSpacingOption>('normal');
  const [lineSpacing, setLineSpacing] = useState<LineSpacingOption>('normal');
  const menuRef = useRef<HTMLDivElement>(null);

  // Load preferences from localStorage on mount
  useEffect(() => {
    // Migrate old dyslexia setting to Lexend font
    const oldDyslexiaSetting = localStorage.getItem(OLD_DYSLEXIA_KEY);
    if (oldDyslexiaSetting === 'true' && !localStorage.getItem(STORAGE_KEY_FONT)) {
      localStorage.setItem(STORAGE_KEY_FONT, 'lexend');
      localStorage.removeItem(OLD_DYSLEXIA_KEY);
    }
    // Clean up old data attributes if present
    document.documentElement.removeAttribute('data-dyslexia-font');
    document.documentElement.removeAttribute('data-reading-width');

    const storedFont = localStorage.getItem(STORAGE_KEY_FONT) as FontOption | null;
    const storedWordSpacing = localStorage.getItem(STORAGE_KEY_WORD_SPACING) as WordSpacingOption | null;
    const storedLineSpacing = localStorage.getItem(STORAGE_KEY_LINE_SPACING) as LineSpacingOption | null;

    if (storedFont) {
      setFont(storedFont);
      document.documentElement.setAttribute('data-reading-font', storedFont);
    }
    if (storedWordSpacing) {
      setWordSpacing(storedWordSpacing);
      document.documentElement.setAttribute('data-reading-word-spacing', storedWordSpacing);
    }
    if (storedLineSpacing) {
      setLineSpacing(storedLineSpacing);
      document.documentElement.setAttribute('data-reading-line-spacing', storedLineSpacing);
    }
  }, []);

  // Close menu on outside click
  useEffect(() => {
    if (variant !== 'dropdown') return;

    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, variant]);

  // Close menu on Escape key
  useEffect(() => {
    if (variant !== 'dropdown') return;

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }
    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, variant]);

  const updateFont = (newFont: FontOption) => {
    setFont(newFont);
    document.documentElement.setAttribute('data-reading-font', newFont);
    localStorage.setItem(STORAGE_KEY_FONT, newFont);
  };

  const updateWordSpacing = (newWordSpacing: WordSpacingOption) => {
    setWordSpacing(newWordSpacing);
    document.documentElement.setAttribute('data-reading-word-spacing', newWordSpacing);
    localStorage.setItem(STORAGE_KEY_WORD_SPACING, newWordSpacing);
  };

  const updateLineSpacing = (newLineSpacing: LineSpacingOption) => {
    setLineSpacing(newLineSpacing);
    document.documentElement.setAttribute('data-reading-line-spacing', newLineSpacing);
    localStorage.setItem(STORAGE_KEY_LINE_SPACING, newLineSpacing);
  };

  const fontOptions: { value: FontOption; label: string }[] = [
    { value: 'default', label: 'Default' },
    { value: 'lexend', label: 'Lexend' },
    { value: 'system', label: 'System' },
  ];

  const wordSpacingOptions: { value: WordSpacingOption; label: string }[] = [
    { value: 'wide', label: 'Wide' },
    { value: 'normal', label: 'Normal' },
    { value: 'narrow', label: 'Tight' },
  ];

  const lineSpacingOptions: { value: LineSpacingOption; label: string }[] = [
    { value: 'relaxed', label: 'Relaxed' },
    { value: 'normal', label: 'Normal' },
    { value: 'compact', label: 'Compact' },
  ];

  const settingsContent = (
    <div className={styles.settingsContent}>
      {/* Font Selection */}
      <div className={styles.settingGroup}>
        <span className={styles.settingLabel}>Font</span>
        <div className={styles.buttonGroup}>
          {fontOptions.map((option) => (
            <button
              key={option.value}
              className={`${styles.optionButton} ${font === option.value ? styles.active : ''}`}
              onClick={() => updateFont(option.value)}
              aria-pressed={font === option.value}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Word Spacing */}
      <div className={styles.settingGroup}>
        <span className={styles.settingLabel}>Word Spacing</span>
        <div className={styles.buttonGroup}>
          {wordSpacingOptions.map((option) => (
            <button
              key={option.value}
              className={`${styles.optionButton} ${wordSpacing === option.value ? styles.active : ''}`}
              onClick={() => updateWordSpacing(option.value)}
              aria-pressed={wordSpacing === option.value}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Line Spacing */}
      <div className={styles.settingGroup}>
        <span className={styles.settingLabel}>Line Spacing</span>
        <div className={styles.buttonGroup}>
          {lineSpacingOptions.map((option) => (
            <button
              key={option.value}
              className={`${styles.optionButton} ${lineSpacing === option.value ? styles.active : ''}`}
              onClick={() => updateLineSpacing(option.value)}
              aria-pressed={lineSpacing === option.value}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  // Panel variant for mobile sidebar - always visible
  if (variant === 'panel') {
    return (
      <div className={styles.panel}>
        <div className={styles.panelHeader}>
          <span className={styles.panelIcon}>Aa</span>
          <span className={styles.panelTitle}>Reading Settings</span>
        </div>
        {settingsContent}
      </div>
    );
  }

  // Dropdown variant for desktop navbar
  return (
    <div className={styles.container} ref={menuRef}>
      <button
        className={styles.trigger}
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-haspopup="true"
        aria-label="Reading settings"
        title="Reading settings"
      >
        <span className={styles.icon}>Aa</span>
        <span className={styles.triggerLabel}>Reading</span>
        <svg
          className={`${styles.chevron} ${isOpen ? styles.chevronOpen : ''}`}
          width="12"
          height="12"
          viewBox="0 0 12 12"
          fill="none"
          aria-hidden="true"
        >
          <path
            d="M2.5 4.5L6 8L9.5 4.5"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {isOpen && (
        <div className={styles.dropdown} role="menu">
          <div className={styles.dropdownHeader}>Reading Settings</div>
          {settingsContent}
        </div>
      )}
    </div>
  );
}
