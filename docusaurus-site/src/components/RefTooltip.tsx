import React, { useState, useRef, useCallback } from 'react';
import styles from './RefTooltip.module.css';

interface RefTooltipProps {
  refNum: string;
  children?: React.ReactNode;
}

// Reference data - this will be populated dynamically
const references: Record<string, string> = {};

export function setReferences(refs: Record<string, string>) {
  Object.assign(references, refs);
}

export default function RefTooltip({ refNum, children }: RefTooltipProps) {
  const [showTooltip, setShowTooltip] = useState(false);
  const hideTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Get the reference text (you'll need to populate this)
  const refText = references[refNum] || 'Reference not found';

  const clearHideTimeout = useCallback(() => {
    if (hideTimeoutRef.current) {
      clearTimeout(hideTimeoutRef.current);
      hideTimeoutRef.current = null;
    }
  }, []);

  const handleMouseEnter = useCallback(() => {
    clearHideTimeout();
    setShowTooltip(true);
  }, [clearHideTimeout]);

  const handleMouseLeave = useCallback(() => {
    hideTimeoutRef.current = setTimeout(() => {
      setShowTooltip(false);
    }, 300);
  }, []);

  const handleFocus = useCallback(() => {
    clearHideTimeout();
    setShowTooltip(true);
  }, [clearHideTimeout]);

  const handleBlur = useCallback(() => {
    hideTimeoutRef.current = setTimeout(() => {
      setShowTooltip(false);
    }, 150);
  }, []);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setShowTooltip(false);
    }
  }, []);

  const tooltipId = `ref-tooltip-${refNum.replace(/\s+/g, '-')}`;

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
            setShowTooltip(!showTooltip);
          }}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          role="button"
          aria-describedby={tooltipId}
        >
          {children || refNum}
        </a>
      </sup>
      {showTooltip && (
        <span
          id={tooltipId}
          role="tooltip"
          className={styles.tooltip}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
          <span className={styles.tooltipContent}>
            <strong>[{refNum}]</strong> {refText}
          </span>
        </span>
      )}
    </span>
  );
}
