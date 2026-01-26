import React, { useState } from 'react';
import ReferenceCard from './ReferenceCard';
import styles from './ReferenceList.module.css';

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

interface ReferenceListProps {
  references: Reference[];
}

export default function ReferenceList({ references }: ReferenceListProps) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredRefs = references.filter(ref => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      ref.authors.toLowerCase().includes(search) ||
      ref.title.toLowerCase().includes(search) ||
      ref.journal?.toLowerCase().includes(search) ||
      ref.year?.includes(search) ||
      ref.num.toString() === search
    );
  });

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.stats}>
          {filteredRefs.length} of {references.length} references
        </div>
        <input
          type="text"
          placeholder="Search references..."
          className={styles.search}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
      <div className={styles.list}>
        {filteredRefs.map(ref => (
          <ReferenceCard key={ref.num} {...ref} />
        ))}
        {filteredRefs.length === 0 && (
          <div className={styles.noResults}>
            No references match your search.
          </div>
        )}
      </div>
    </div>
  );
}
