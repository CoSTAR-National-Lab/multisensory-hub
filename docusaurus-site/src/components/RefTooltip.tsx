import React, { useState } from 'react';
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

  // Get the reference text (you'll need to populate this)
  const refText = references[refNum] || 'Reference not found';

  return (
    <span
      className={styles.refContainer}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
      onClick={(e) => {
        e.preventDefault();
        setShowTooltip(!showTooltip);
      }}
    >
      <sup>
        <a
          href={`/references#ref-${refNum}`}
          className={styles.refLink}
          onClick={(e) => e.preventDefault()}
        >
          {children || refNum}
        </a>
      </sup>
      {showTooltip && (
        <span className={styles.tooltip}>
          <span className={styles.tooltipContent}>
            <strong>[{refNum}]</strong> {refText}
          </span>
        </span>
      )}
    </span>
  );
}
