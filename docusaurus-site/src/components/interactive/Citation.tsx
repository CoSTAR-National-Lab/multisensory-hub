import React, { useState } from 'react';
import styles from './Citation.module.css';

interface Reference {
  num: number;
  authors: string;
  title: string;
  journal?: string;
  year?: string;
  volume?: string;
  pages?: string;
  doi?: string;
  url?: string;
}

interface CitationProps {
  num: number;
  references: Reference[];
}

export default function Citation({ num, references }: CitationProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  const ref = references.find(r => r.num === num);

  if (!ref) {
    return <sup className={styles.citation}>{num}</sup>;
  }

  return (
    <span
      className={styles.citationWrapper}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <sup className={styles.citation}>{num}</sup>
      {showTooltip && (
        <div className={styles.tooltip}>
          <div className={styles.tooltipContent}>
            <span className={styles.refNumber}>[{ref.num}]</span>
            <span className={styles.authors}>{ref.authors}</span>
            <span className={styles.title}>{ref.title}</span>
            {ref.journal && (
              <span className={styles.journal}>
                {ref.journal}
                {ref.volume && ` ${ref.volume}`}
                {ref.pages && `, ${ref.pages}`}
                {ref.year && ` (${ref.year})`}
              </span>
            )}
            {ref.doi && (
              <a
                href={`https://doi.org/${ref.doi}`}
                className={styles.doi}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
              >
                DOI: {ref.doi}
              </a>
            )}
            {ref.url && !ref.doi && (
              <a
                href={ref.url}
                className={styles.url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
              >
                Link
              </a>
            )}
          </div>
        </div>
      )}
    </span>
  );
}
