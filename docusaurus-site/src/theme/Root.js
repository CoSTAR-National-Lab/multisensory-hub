import React from 'react';

export default function Root({children}) {
  return (
    <>
      <a
        href="#__docusaurus_skipToContent_fallback"
        className="skip-to-content sr-only"
      >
        Skip to main content
      </a>
      {children}
    </>
  );
}
