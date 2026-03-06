import React, { useState } from 'react';
import styles from './ReferenceCard.module.css';

interface ReferenceCardProps {
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

// Helper to render text with clickable URLs
function renderWithLinks(text: string): React.ReactNode {
  if (!text) return text;

  // Match URLs in text
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  const parts = text.split(urlRegex);

  if (parts.length === 1) return text;

  return parts.map((part, index) => {
    if (part.match(urlRegex)) {
      return (
        <a
          key={index}
          href={part}
          target="_blank"
          rel="noopener noreferrer"
          className={styles.inlineLink}
          onClick={(e) => e.stopPropagation()}
        >
          {part}
        </a>
      );
    }
    return part;
  });
}

export default function ReferenceCard({
  num,
  authors,
  title,
  journal,
  year,
  volume,
  pages,
  doi,
  url,
}: ReferenceCardProps) {
  const [copied, setCopied] = useState(false);

  const titleHref = doi ? `https://doi.org/${doi}` : url || null;
  const titleHasInlineUrl = /https?:\/\//.test(title || '');

  // Format reference for copying
  const formatReferenceText = (): string => {
    const parts: string[] = [];
    if (authors) parts.push(authors);
    if (title) parts.push(title);
    if (journal) parts.push(journal);
    if (volume) parts.push(volume);
    if (pages) parts.push(pages);
    if (year) parts.push(`(${year})`);
    if (doi) parts.push(`doi:${doi}`);
    else if (url) parts.push(url);
    return `[${num}] ${parts.join('. ').replace(/\.\./g, '.')}`;
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(formatReferenceText());
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className={styles.card} id={`ref-${num}`}>
      <div className={styles.content}>
        <div className={styles.actions}>
          {doi && (
            <a
              href={`https://doi.org/${doi}`}
              className={styles.actionIcon}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={`Open DOI link: ${doi}`}
              title={`DOI: ${doi}`}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
                <path d="M4.715 6.542L3.343 7.914a3 3 0 104.243 4.243l1.828-1.829A3 3 0 008.586 5.5L8 6.086a1.001 1.001 0 00-.154.199 2 2 0 01.861 3.337L6.88 11.45a2 2 0 11-2.83-2.83l.793-.792a4.018 4.018 0 01-.128-1.287z"/>
                <path d="M6.586 4.672A3 3 0 007.414 9.5l.775-.776a2 2 0 01-.896-3.346L9.12 3.55a2 2 0 012.83 2.83l-.793.792c.112.42.155.855.128 1.287l1.372-1.372a3 3 0 00-4.243-4.243L6.586 4.672z"/>
              </svg>
            </a>
          )}
          {url && !doi && (
            <a
              href={url}
              className={styles.actionIcon}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="View source URL"
              title="View source"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
                <path d="M4.715 6.542L3.343 7.914a3 3 0 104.243 4.243l1.828-1.829A3 3 0 008.586 5.5L8 6.086a1.001 1.001 0 00-.154.199 2 2 0 01.861 3.337L6.88 11.45a2 2 0 11-2.83-2.83l.793-.792a4.018 4.018 0 01-.128-1.287z"/>
                <path d="M6.586 4.672A3 3 0 007.414 9.5l.775-.776a2 2 0 01-.896-3.346L9.12 3.55a2 2 0 012.83 2.83l-.793.792c.112.42.155.855.128 1.287l1.372-1.372a3 3 0 00-4.243-4.243L6.586 4.672z"/>
              </svg>
            </a>
          )}
          <button
            className={styles.actionIcon}
            onClick={handleCopy}
            aria-label={copied ? "Reference copied" : "Copy reference"}
            title={copied ? "Copied!" : "Copy reference"}
          >
            {copied ? (
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
                <path d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z"/>
              </svg>
            ) : (
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
                <path d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 010 1.5h-1.5a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-1.5a.75.75 0 011.5 0v1.5A1.75 1.75 0 019.25 16h-7.5A1.75 1.75 0 010 14.25v-7.5z"/>
                <path d="M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0114.25 11h-7.5A1.75 1.75 0 015 9.25v-7.5zm1.75-.25a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-7.5a.25.25 0 00-.25-.25h-7.5z"/>
              </svg>
            )}
          </button>
        </div>
        {authors ? (
          <>
            <div className={styles.authors}><span className={styles.numLabel}>[{num}]</span>{renderWithLinks(authors)}</div>
            <div className={styles.title}>
              {titleHref && !titleHasInlineUrl ? (
                <a href={titleHref} target="_blank" rel="noopener noreferrer" className={styles.titleLink}>{title}</a>
              ) : renderWithLinks(title)}
            </div>
          </>
        ) : (
          <div className={styles.title}>
            <span className={styles.numLabel}>[{num}]</span>
            {titleHref && !titleHasInlineUrl ? (
              <a href={titleHref} target="_blank" rel="noopener noreferrer" className={styles.titleLink}>{title}</a>
            ) : renderWithLinks(title)}
          </div>
        )}
        {journal && (
          <div className={styles.publication}>
            <span className={styles.journal}>{renderWithLinks(journal)}</span>
            {volume && <span className={styles.volume}> {volume}</span>}
            {pages && <span className={styles.pages}>, {pages}</span>}
            {year && <span className={styles.year}> ({year})</span>}
          </div>
        )}
        {!journal && year && (
          <div className={styles.publication}>
            <span className={styles.year}>({year})</span>
          </div>
        )}
      </div>
    </div>
  );
}
