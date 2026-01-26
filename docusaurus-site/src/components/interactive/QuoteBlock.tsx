import React from 'react';
import styles from './QuoteBlock.module.css';

interface QuoteBlockProps {
  children: React.ReactNode;
  author?: string;
  source?: string;
}

export default function QuoteBlock({ children, author, source }: QuoteBlockProps) {
  return (
    <figure className={styles.quote}>
      <div className={styles.quoteIcon}>"</div>
      <blockquote className={styles.content}>
        {children}
      </blockquote>
      {(author || source) && (
        <figcaption className={styles.attribution}>
          {author && <span className={styles.author}>— {author}</span>}
          {source && <cite className={styles.source}>, {source}</cite>}
        </figcaption>
      )}
    </figure>
  );
}
