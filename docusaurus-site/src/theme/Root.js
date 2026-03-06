import React from 'react';
import {DocsPreferredVersionContextProvider} from '@docusaurus/plugin-content-docs/client';

export default function Root({children}) {
  return (
    <DocsPreferredVersionContextProvider>
      <a
        href="#__docusaurus_skipToContent_fallback"
        className="skip-to-content sr-only"
      >
        Skip to main content
      </a>
      {children}
    </DocsPreferredVersionContextProvider>
  );
}
