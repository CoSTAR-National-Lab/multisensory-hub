import React, { createContext, useCallback, useContext, useEffect, useRef } from 'react';
import { useLocation } from '@docusaurus/router';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

const OPTOUT_KEY = 'concept_analytics_optout';
const SESSION_KEY = 'concept_analytics_session_id';
const HEARTBEAT_MS = 15_000;
const IDLE_MS = 60_000;

interface AnalyticsContextValue {
  trackEvent: (eventType: string, data?: Record<string, unknown>) => void;
  isIdle: () => boolean;
}

const AnalyticsContext = createContext<AnalyticsContextValue>({
  trackEvent: () => {},
  isIdle: () => false,
});
export const useAnalytics = () => useContext(AnalyticsContext);

function isOptedOut(): boolean {
  try {
    return localStorage.getItem(OPTOUT_KEY) === '1';
  } catch { return false; }
}

function getOrCreateSessionId(): string {
  try {
    let sid = sessionStorage.getItem(SESSION_KEY);
    if (!sid) { sid = crypto.randomUUID(); sessionStorage.setItem(SESSION_KEY, sid); }
    return sid;
  } catch { return 'fallback-' + Date.now(); }
}

function getReferrerDomain(): string {
  try {
    const ref = document.referrer;
    return ref ? new URL(ref).hostname : '';
  } catch { return ''; }
}

const LOCAL_ENDPOINT = 'http://127.0.0.1:8000/analytics/ingest/';
const PROD_ENDPOINT  = 'https://costartools.uk/analytics/ingest/';

function deriveEndpoint(): string {
  if (typeof window === 'undefined') return '';  // SSR guard
  const { hostname } = window.location;
  return hostname === 'localhost' || hostname === '127.0.0.1'
    ? LOCAL_ENDPOINT
    : PROD_ENDPOINT;
}

export default function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  const { siteConfig } = useDocusaurusContext();
  const endpoint = deriveEndpoint();
  const manifestVersion = (siteConfig.customFields?.analyticsManifestVersion as string) || '';
  const location = useLocation();

  const sessionId    = useRef('');
  const queue        = useRef<Record<string, unknown>[]>([]);
  const sequence     = useRef(0);
  const currentPath  = useRef('');
  const prevPath     = useRef('');
  const heartbeat    = useRef<ReturnType<typeof setInterval> | null>(null);
  const referrerDomain = useRef('');
  const viewport     = useRef({ width: 0, height: 0 });

  // Idle detection
  const lastActivityAt = useRef(Date.now());
  const idleRef        = useRef(false);

  const active = useCallback(() => !!endpoint && !isOptedOut(), [endpoint]);
  const isIdle = useCallback(() => idleRef.current, []);

  const enqueue = useCallback((eventType: string, data: Record<string, unknown> = {}) => {
    if (!active()) return;
    queue.current.push({ event_sequence: ++sequence.current, event_type: eventType, ...data });
  }, [active]);

  const flush = useCallback((beacon: boolean) => {
    if (!active() || queue.current.length === 0) return;
    const events = queue.current.splice(0);
    const payload = {
      session_id: sessionId.current,
      page_path: currentPath.current,
      page_title: typeof document !== 'undefined' ? document.title : '',
      referrer_domain: referrerDomain.current,
      viewport: viewport.current,
      manifest_version: manifestVersion,
      events,
    };
    if (beacon && typeof navigator !== 'undefined' && navigator.sendBeacon) {
      navigator.sendBeacon(endpoint, new Blob([JSON.stringify(payload)], { type: 'text/plain' }));
    } else {
      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      }).catch(() => {});
    }
  }, [active, endpoint]);

  // Session init — once on mount
  useEffect(() => {
    console.log('[Analytics] session init effect — endpoint:', endpoint, 'active:', active());
    if (!active()) return;
    sessionId.current = getOrCreateSessionId();
    referrerDomain.current = getReferrerDomain();
    viewport.current = { width: window.innerWidth, height: window.innerHeight };
    enqueue('session_start');
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Idle detection
  useEffect(() => {
    if (!active()) return;
    const onActivity = () => { lastActivityAt.current = Date.now(); idleRef.current = false; };
    const activityEvents = ['scroll', 'click', 'keydown', 'pointermove', 'touchstart'] as const;
    activityEvents.forEach(e => window.addEventListener(e, onActivity, { passive: true }));
    const idleCheck = setInterval(() => {
      idleRef.current = Date.now() - lastActivityAt.current > IDLE_MS;
    }, 10_000);
    return () => {
      activityEvents.forEach(e => window.removeEventListener(e, onActivity));
      clearInterval(idleCheck);
    };
  }, [active]);

  // Route changes
  useEffect(() => {
    if (!active()) return;
    if (prevPath.current && prevPath.current !== location.pathname) flush(false);
    currentPath.current = location.pathname;
    prevPath.current = location.pathname;
    enqueue('page_view', { page_path: location.pathname });
  }, [location.pathname, active, enqueue, flush]);

  // Visibility changes
  useEffect(() => {
    if (!active()) return;
    const handler = () => {
      if (document.visibilityState === 'hidden') {
        enqueue('page_hidden');
        flush(true);
      } else {
        enqueue('session_resume', { resume_reason: 'visibility' });
      }
    };
    document.addEventListener('visibilitychange', handler);
    return () => document.removeEventListener('visibilitychange', handler);
  }, [active, enqueue, flush]);

  // Page-level heartbeat
  useEffect(() => {
    if (!active()) return;
    heartbeat.current = setInterval(() => {
      if (document.visibilityState === 'visible' && !idleRef.current) {
        enqueue('page_visible_heartbeat', { page_path: currentPath.current });
        flush(false);
      }
    }, HEARTBEAT_MS);
    return () => { if (heartbeat.current) clearInterval(heartbeat.current); };
  }, [active, enqueue, flush]);

  // Page unload
  useEffect(() => {
    if (!active()) return;
    const handler = () => { enqueue('page_unload'); flush(true); };
    window.addEventListener('pagehide', handler);
    return () => window.removeEventListener('pagehide', handler);
  }, [active, enqueue, flush]);

  return (
    <AnalyticsContext.Provider value={{ trackEvent: enqueue, isIdle }}>
      {children}
    </AnalyticsContext.Provider>
  );
}
