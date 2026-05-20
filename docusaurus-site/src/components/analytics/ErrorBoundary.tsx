import React from 'react';

interface State { hasError: boolean; }

export default class ErrorBoundary extends React.Component<{ children: React.ReactNode }, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('Analytics error (site continues normally):', error, info);
  }

  render() {
    // Always render children — analytics failures must not affect the Hub
    return this.props.children;
  }
}
