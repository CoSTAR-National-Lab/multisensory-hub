import React from 'react';
import styles from './Callout.module.css';

type CalloutType = 'info' | 'warning' | 'success' | 'tip' | 'note';

interface CalloutProps {
  type?: CalloutType;
  title?: string;
  children: React.ReactNode;
}

const icons: Record<CalloutType, { emoji: string; label: string }> = {
  info: { emoji: '💡', label: 'Information' },
  warning: { emoji: '⚠️', label: 'Warning' },
  success: { emoji: '✅', label: 'Success' },
  tip: { emoji: '🎯', label: 'Tip' },
  note: { emoji: '📝', label: 'Note' },
};

export default function Callout({ type = 'info', title, children }: CalloutProps) {
  const { emoji, label } = icons[type];
  const role = type === 'warning' ? 'alert' : 'note';

  return (
    <div className={`${styles.callout} ${styles[type]}`} role={role}>
      <div className={styles.header}>
        <span 
          className={styles.icon} 
          role="img" 
          aria-label={label}
        >
          {emoji}
        </span>
        {title && <span className={styles.title}>{title}</span>}
      </div>
      <div className={styles.content}>{children}</div>
    </div>
  );
}
