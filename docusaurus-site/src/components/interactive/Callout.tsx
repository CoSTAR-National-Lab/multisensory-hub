import React from 'react';
import styles from './Callout.module.css';

type CalloutType = 'info' | 'warning' | 'success' | 'tip' | 'note';

interface CalloutProps {
  type?: CalloutType;
  title?: string;
  children: React.ReactNode;
}

const icons: Record<CalloutType, string> = {
  info: '💡',
  warning: '⚠️',
  success: '✅',
  tip: '🎯',
  note: '📝',
};

export default function Callout({ type = 'info', title, children }: CalloutProps) {
  return (
    <div className={`${styles.callout} ${styles[type]}`}>
      <div className={styles.header}>
        <span className={styles.icon}>{icons[type]}</span>
        {title && <span className={styles.title}>{title}</span>}
      </div>
      <div className={styles.content}>{children}</div>
    </div>
  );
}
