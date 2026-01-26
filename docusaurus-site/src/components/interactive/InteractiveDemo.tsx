import React, { useState } from 'react';
import styles from './InteractiveDemo.module.css';

interface InteractiveDemoProps {
  title?: string;
  description?: string;
  children?: React.ReactNode;
}

export default function InteractiveDemo({
  title = 'Interactive Demo',
  description,
  children
}: InteractiveDemoProps) {
  const [isActive, setIsActive] = useState(false);

  return (
    <div className={`${styles.demo} ${isActive ? styles.active : ''}`}>
      <div className={styles.header}>
        <div className={styles.titleRow}>
          <span className={styles.badge}>Interactive</span>
          <h4 className={styles.title}>{title}</h4>
        </div>
        {description && <p className={styles.description}>{description}</p>}
      </div>
      <div className={styles.content}>
        {children || (
          <div className={styles.placeholder}>
            <div className={styles.placeholderIcon}>🎮</div>
            <p>Interactive content placeholder</p>
            <button
              className={styles.button}
              onClick={() => setIsActive(!isActive)}
            >
              {isActive ? 'Deactivate' : 'Try it out'}
            </button>
          </div>
        )}
      </div>
      {isActive && (
        <div className={styles.overlay}>
          <div className={styles.particles}>
            {[...Array(20)].map((_, i) => (
              <span
                key={i}
                className={styles.particle}
                style={{
                  left: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 2}s`,
                  animationDuration: `${2 + Math.random() * 2}s`
                }}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
