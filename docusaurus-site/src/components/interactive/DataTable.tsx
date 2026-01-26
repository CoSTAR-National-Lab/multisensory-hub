import React, { useState, useMemo } from 'react';
import styles from './DataTable.module.css';

interface DataTableProps {
  data: Record<string, any>[];
  columns?: string[];
  sortable?: boolean;
  searchable?: boolean;
}

export default function DataTable({
  data,
  columns,
  sortable = true,
  searchable = true
}: DataTableProps) {
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [searchTerm, setSearchTerm] = useState('');

  const headers = columns || (data.length > 0 ? Object.keys(data[0]) : []);

  const filteredAndSortedData = useMemo(() => {
    let result = [...data];

    if (searchTerm) {
      result = result.filter(row =>
        headers.some(header =>
          String(row[header]).toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    if (sortColumn) {
      result.sort((a, b) => {
        const aVal = a[sortColumn];
        const bVal = b[sortColumn];
        const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
        return sortDirection === 'asc' ? comparison : -comparison;
      });
    }

    return result;
  }, [data, searchTerm, sortColumn, sortDirection, headers]);

  const handleSort = (column: string) => {
    if (!sortable) return;
    if (sortColumn === column) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  return (
    <div className={styles.tableContainer}>
      {searchable && (
        <div className={styles.searchBar}>
          <input
            type="text"
            placeholder="Search..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={styles.searchInput}
          />
        </div>
      )}
      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              {headers.map(header => (
                <th
                  key={header}
                  onClick={() => handleSort(header)}
                  className={sortable ? styles.sortable : ''}
                >
                  <span>{header}</span>
                  {sortColumn === header && (
                    <span className={styles.sortIndicator}>
                      {sortDirection === 'asc' ? ' ↑' : ' ↓'}
                    </span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredAndSortedData.map((row, idx) => (
              <tr key={idx} className={styles.row}>
                {headers.map(header => (
                  <td key={header}>{row[header]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className={styles.footer}>
        Showing {filteredAndSortedData.length} of {data.length} rows
      </div>
    </div>
  );
}
