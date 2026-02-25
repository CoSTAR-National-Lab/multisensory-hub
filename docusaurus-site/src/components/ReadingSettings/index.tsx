import React, { useState, useEffect, useRef } from 'react';
import { useColorMode } from '@docusaurus/theme-common';
import styles from './styles.module.css';

const STORAGE_KEY_FONT = 'reading-settings-font';
const STORAGE_KEY_WORD_SPACING = 'reading-settings-word-spacing';
const STORAGE_KEY_LINE_SPACING = 'reading-settings-line-spacing';
const STORAGE_KEY_CONTRAST = 'reading-settings-contrast';
const STORAGE_KEY_TEXT_SIZE = 'reading-settings-text-size';
const STORAGE_KEY_MOTION = 'reading-settings-motion';
const OLD_DYSLEXIA_KEY = 'dyslexia-font-enabled';

type FontOption = 'default' | 'lexend' | 'system';
type WordSpacingOption = 'wide' | 'normal' | 'narrow';
type LineSpacingOption = 'relaxed' | 'normal' | 'compact';
type ContrastOption = 'standard' | 'low' | 'high';
type TextSizeOption = 'standard' | 'large' | 'xl';
type MotionOption = 'standard' | 'reduced';

interface ReadingSettingsProps {
  /** If true, renders as a panel instead of dropdown (for mobile sidebar) */
  variant?: 'dropdown' | 'panel';
}

export default function ReadingSettings({ variant = 'dropdown' }: ReadingSettingsProps): JSX.Element {
  const { colorMode, setColorMode } = useColorMode();
  const [isOpen, setIsOpen] = useState(false);
  const [font, setFont] = useState<FontOption>('default');
  const [wordSpacing, setWordSpacing] = useState<WordSpacingOption>('normal');
  const [lineSpacing, setLineSpacing] = useState<LineSpacingOption>('normal');
  const [contrast, setContrast] = useState<ContrastOption>('standard');
  const [textSize, setTextSize] = useState<TextSizeOption>('standard');
  const [motion, setMotion] = useState<MotionOption>('standard');
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
    const storedContrast = localStorage.getItem(STORAGE_KEY_CONTRAST) as ContrastOption | null;
    const storedTextSize = localStorage.getItem(STORAGE_KEY_TEXT_SIZE) as TextSizeOption | null;
    const storedMotion = localStorage.getItem(STORAGE_KEY_MOTION) as MotionOption | null;

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
    if (storedContrast) {
      setContrast(storedContrast);
      document.documentElement.setAttribute('data-accessibility-contrast', storedContrast);
    }
    if (storedTextSize) {
      setTextSize(storedTextSize);
      document.documentElement.setAttribute('data-accessibility-text-size', storedTextSize);
    }
    if (storedMotion) {
      setMotion(storedMotion);
      document.documentElement.setAttribute('data-accessibility-motion', storedMotion);
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

  const updateContrast = (newContrast: ContrastOption) => {
    setContrast(newContrast);
    document.documentElement.setAttribute('data-accessibility-contrast', newContrast);
    localStorage.setItem(STORAGE_KEY_CONTRAST, newContrast);
  };

  const updateTextSize = (newTextSize: TextSizeOption) => {
    setTextSize(newTextSize);
    document.documentElement.setAttribute('data-accessibility-text-size', newTextSize);
    localStorage.setItem(STORAGE_KEY_TEXT_SIZE, newTextSize);
  };

  const updateMotion = (newMotion: MotionOption) => {
    setMotion(newMotion);
    document.documentElement.setAttribute('data-accessibility-motion', newMotion);
    localStorage.setItem(STORAGE_KEY_MOTION, newMotion);
  };

  const resetToDefaults = () => {
    setFont('default');
    setWordSpacing('normal');
    setLineSpacing('normal');
    setContrast('standard');
    setTextSize('standard');
    setMotion('standard');

    document.documentElement.setAttribute('data-reading-font', 'default');
    document.documentElement.setAttribute('data-reading-word-spacing', 'normal');
    document.documentElement.setAttribute('data-reading-line-spacing', 'normal');
    document.documentElement.removeAttribute('data-accessibility-contrast');
    document.documentElement.removeAttribute('data-accessibility-text-size');
    document.documentElement.removeAttribute('data-accessibility-motion');

    [
      STORAGE_KEY_FONT,
      STORAGE_KEY_WORD_SPACING,
      STORAGE_KEY_LINE_SPACING,
      STORAGE_KEY_CONTRAST,
      STORAGE_KEY_TEXT_SIZE,
      STORAGE_KEY_MOTION,
    ].forEach((key) => localStorage.removeItem(key));
  };

  const contrastOptions: { value: ContrastOption; label: string }[] = [
    { value: 'standard', label: 'Standard' },
    { value: 'low', label: 'Low' },
    { value: 'high', label: 'High' },
  ];

  const textSizeOptions: { value: TextSizeOption; label: string }[] = [
    { value: 'standard', label: 'Standard' },
    { value: 'large', label: 'Large' },
    { value: 'xl', label: 'Extra Large' },
  ];

  const motionOptions: { value: MotionOption; label: string }[] = [
    { value: 'standard', label: 'Standard' },
    { value: 'reduced', label: 'Reduced' },
  ];

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
      <p className={styles.subtitle}>Adjust how this site looks to suit your needs.</p>

      {/* Theme */}
      <div className={styles.settingGroup}>
        <span className={styles.settingLabel}>Theme</span>
        <div className={styles.buttonGroup}>
          <button
            className={`${styles.optionButton} ${colorMode === 'light' ? styles.active : ''}`}
            onClick={() => setColorMode('light')}
            aria-pressed={colorMode === 'light'}
          >
            Light
          </button>
          <button
            className={`${styles.optionButton} ${colorMode === 'dark' ? styles.active : ''}`}
            onClick={() => setColorMode('dark')}
            aria-pressed={colorMode === 'dark'}
          >
            Dark
          </button>
        </div>
      </div>

      {/* Contrast */}
      <div className={styles.settingGroup}>
        <span className={styles.settingLabel}>Contrast</span>
        <div className={styles.buttonGroup}>
          {contrastOptions.map((option) => (
            <button
              key={option.value}
              className={`${styles.optionButton} ${contrast === option.value ? styles.active : ''}`}
              onClick={() => updateContrast(option.value)}
              aria-pressed={contrast === option.value}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Text Size */}
      <div className={styles.settingGroup}>
        <span className={styles.settingLabel}>Text Size</span>
        <div className={styles.buttonGroup}>
          {textSizeOptions.map((option) => (
            <button
              key={option.value}
              className={`${styles.optionButton} ${textSize === option.value ? styles.active : ''}`}
              onClick={() => updateTextSize(option.value)}
              aria-pressed={textSize === option.value}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Motion */}
      <div className={styles.settingGroup}>
        <span className={styles.settingLabel}>Motion</span>
        <div className={styles.buttonGroup}>
          {motionOptions.map((option) => (
            <button
              key={option.value}
              className={`${styles.optionButton} ${motion === option.value ? styles.active : ''}`}
              onClick={() => updateMotion(option.value)}
              aria-pressed={motion === option.value}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Font */}
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

      <button className={styles.resetButton} onClick={resetToDefaults}>
        Reset to defaults
      </button>
    </div>
  );

  // Panel variant for mobile sidebar - always visible
  if (variant === 'panel') {
    return (
      <div className={styles.panel}>
        <div className={styles.panelHeader}>
          <span className={styles.panelIcon}>Aa</span>
          <span className={styles.panelTitle}>Accessibility</span>
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
        aria-haspopup="dialog"
        aria-label="Accessibility settings"
        title="Accessibility settings"
      >
        <span className={styles.icon}>Aa</span>
        <span className={styles.triggerLabel}>Accessibility</span>
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
        <div
          className={styles.dropdown}
          role="dialog"
          aria-label="Accessibility settings"
        >
          <div className={styles.dropdownHeader}>
            <span className={styles.dropdownTitle}>Accessibility</span>
            <button
              className={styles.closeButton}
              onClick={() => setIsOpen(false)}
              aria-label="Close accessibility settings"
            >
              ×
            </button>
          </div>
          {settingsContent}
        </div>
      )}
    </div>
  );
}
