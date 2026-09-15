import React, { useState, useRef, useCallback } from 'react';
import styles from './RefPopup.module.css';
import { references, Reference } from '@site/src/data/references';

interface RefPopupProps {
  refNum: string;
  refText?: string;
}

/** "25,26" -> [25, 26]; "20-22" (any dash) -> [20, 21, 22]; ranges capped at 25 items. */
export function expandRefNums(refNum: string): number[] {
  const out: number[] = [];
  for (const part of refNum.split(',')) {
    const range = part.trim().match(/^(\d+)\s*[-\u2013\u2014]\s*(\d+)$/);
    if (range) {
      const a = parseInt(range[1], 10);
      const b = Math.min(parseInt(range[2], 10), a + 24);
      for (let n = a; n <= b; n++) out.push(n);
    } else {
      const n = parseInt(part, 10);
      if (!Number.isNaN(n)) out.push(n);
    }
  }
  return out.length ? out : [NaN];
}

export default function RefPopup({ refNum, refText }: RefPopupProps) {
  const [showPopup, setShowPopup] = useState(false);
  const [copied, setCopied] = useState(false);
  const hideTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // A citation may cover several references: "25,26" or a range "20-22".
  // Expand to the full list so the popup shows every one of them.
  const nums = expandRefNums(refNum);
  const primaryNum = nums[0];
  const entries = nums.map(n => ({ num: n, ref: references.find(r => r.num === n) }));

  // Format the reference for display
  const formatReference = (ref: Reference): string => {
    const parts: string[] = [];
    if (ref.authors) parts.push(ref.authors);
    if (ref.title) parts.push(ref.title);
    if (ref.journal) parts.push(`*${ref.journal}*`);
    if (ref.volume) parts.push(ref.volume);
    if (ref.pages) parts.push(ref.pages);
    if (ref.year) parts.push(`(${ref.year})`);
    return parts.join('. ').replace(/\.\./g, '.');
  };

  const displayText = entries
    .map(({ num, ref }) => `[${num}] ${ref ? formatReference(ref) : refText || `Reference ${num}`}`)
    .join('\n');

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(displayText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleGoToRef = () => {
    window.location.href = `/references#ref-${primaryNum}`;
  };

  const clearHideTimeout = useCallback(() => {
    if (hideTimeoutRef.current) {
      clearTimeout(hideTimeoutRef.current);
      hideTimeoutRef.current = null;
    }
  }, []);

  const handleMouseEnter = useCallback(() => {
    clearHideTimeout();
    setShowPopup(true);
  }, [clearHideTimeout]);

  const handleMouseLeave = useCallback(() => {
    // Longer delay so user can move to the centred popup
    hideTimeoutRef.current = setTimeout(() => {
      setShowPopup(false);
    }, 800);
  }, []);

  const handleFocus = useCallback(() => {
    clearHideTimeout();
    setShowPopup(true);
  }, [clearHideTimeout]);

  const handleBlur = useCallback(() => {
    // Delay hiding so user can move focus to elements inside the popup
    hideTimeoutRef.current = setTimeout(() => {
      setShowPopup(false);
    }, 150);
  }, []);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setShowPopup(false);
    }
  }, []);

  const popupId = `ref-popup-${refNum.replace(/\s+/g, '-')}`;

  return (
    <span
      className={styles.refContainer}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <sup>
        <a
          href={`/references#ref-${refNum}`}
          className={styles.refLink}
          onClick={(e) => {
            e.preventDefault();
            setShowPopup(!showPopup);
          }}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          role="button"
          aria-describedby={popupId}
        >
          {refNum}
        </a>
      </sup>

      {showPopup && (
        <>
        <div
          className={styles.overlay}
          onClick={() => setShowPopup(false)}
          aria-hidden="true"
        />
        <div
          id={popupId}
          role="tooltip"
          className={styles.popup}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
          <div className={styles.popupContent}>
            {entries.map(({ num, ref }) => (
              <div key={num} className={styles.refItem}>
                <div className={styles.refNumber}>[{num}]</div>
                {ref ? (
                  <div className={styles.refDetails}>
                    {ref.authors && (
                      <div className={styles.refAuthors}>{ref.authors}</div>
                    )}
                    {ref.title && (
                      <div className={styles.refTitle}>{ref.title}</div>
                    )}
                    <div className={styles.refMeta}>
                      {ref.journal && <span className={styles.refJournal}>{ref.journal}</span>}
                      {ref.volume && <span>, {ref.volume}</span>}
                      {ref.pages && <span>: {ref.pages}</span>}
                      {ref.year && <span> ({ref.year})</span>}
                    </div>
                    {(ref.doi || ref.url) && (
                      <div className={styles.refLinks}>
                        {ref.doi && (
                          <a
                            href={`https://doi.org/${ref.doi}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className={styles.doiLink}
                            onClick={(e) => e.stopPropagation()}
                          >
                            DOI: {ref.doi}
                          </a>
                        )}
                        {!ref.doi && ref.url && (
                          <a
                            href={ref.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className={styles.urlLink}
                            onClick={(e) => e.stopPropagation()}
                          >
                            {ref.url.length > 50 ? ref.url.substring(0, 50) + '...' : ref.url}
                          </a>
                        )}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className={styles.refText}>{refText || `Reference ${num}`}</div>
                )}
              </div>
            ))}
            <div className={styles.actions}>
              <button
                className={styles.actionButton}
                onClick={handleCopy}
                aria-label={entries.length > 1 ? "Copy references" : "Copy reference"}
              >
                {copied ? (
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" className={styles.copied} aria-hidden="true">
                    <path d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z"/>
                  </svg>
                ) : (
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
                    <path d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 010 1.5h-1.5a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-1.5a.75.75 0 011.5 0v1.5A1.75 1.75 0 019.25 16h-7.5A1.75 1.75 0 010 14.25v-7.5z"/>
                    <path d="M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0114.25 11h-7.5A1.75 1.75 0 015 9.25v-7.5zm1.75-.25a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-7.5a.25.25 0 00-.25-.25h-7.5z"/>
                  </svg>
                )}
                <span>{copied ? 'Copied!' : 'Copy'}</span>
              </button>
              <button
                className={styles.actionButton}
                onClick={handleGoToRef}
                aria-label="Go to references page"
              >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
                  <path d="M3.75 2a.75.75 0 01.75.75v7.5a.75.75 0 01-1.5 0v-7.5A.75.75 0 013.75 2zm8.5 0a.75.75 0 01.75.75v7.5a.75.75 0 01-1.5 0v-7.5a.75.75 0 01.75-.75zm-5 1.5a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5a.75.75 0 01.75-.75z"/>
                  <path d="M8 11a.75.75 0 01.75.75v2.5a.75.75 0 01-1.5 0v-2.5A.75.75 0 018 11z"/>
                </svg>
                <span>View all</span>
              </button>
            </div>
          </div>
        </div>
        </>
      )}
    </span>
  );
}
