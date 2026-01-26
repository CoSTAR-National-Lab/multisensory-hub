import React from 'react';
import Content from '@theme-original/DocItem/Content';
import {useDoc} from '@docusaurus/plugin-content-docs/client';
import styles from './styles.module.css';

export default function ContentWrapper(props) {
  const {metadata} = useDoc();
  const readingTime = metadata.frontMatter.readingTimeMinutes;

  return (
    <>
      {readingTime && (
        <div className={styles.readingTime}>
          <span className={styles.readingTimeIcon}>⏱️</span>
          {readingTime} {readingTime === 1 ? 'minute' : 'minutes'} read
        </div>
      )}
      <Content {...props} />
    </>
  );
}
