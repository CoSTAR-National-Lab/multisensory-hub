import React from 'react';
import {DocsPreferredVersionContextProvider} from '@docusaurus/plugin-content-docs/client';
import AnalyticsProvider from '../components/analytics/AnalyticsProvider';
import ErrorBoundary from '../components/analytics/ErrorBoundary';

export default function Root({children}) {
  return (
    <DocsPreferredVersionContextProvider>
      <a
        href="#__docusaurus_skipToContent_fallback"
        className="skip-to-content sr-only"
      >
        Skip to main content
      </a>
      <ErrorBoundary>
        <AnalyticsProvider>
          {children}
        </AnalyticsProvider>
      </ErrorBoundary>
    </DocsPreferredVersionContextProvider>
  );
}
