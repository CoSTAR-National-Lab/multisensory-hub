import React, { useCallback, useEffect, useRef } from 'react';
import { useAnalytics } from '../analytics/AnalyticsProvider';

interface TrackedBlockProps {
  blockId: string;
  topic?: string;
  concept?: string;
  contentType?: string;
  label?: string;
  children: React.ReactNode;
}

const DWELL_THRESHOLD_MS = 3_000;
const HEARTBEAT_MS = 15_000;
const VISIBILITY_RATIO = 0.5;

export default function TrackedBlock({ blockId, topic, concept, contentType, label, children }: TrackedBlockProps) {
  const { trackEvent, isIdle } = useAnalytics();
  const ref = useRef<HTMLDivElement>(null);

  const blockMeta = { block_id: blockId, topic, concept, content_type: contentType, label };

  const visibleSince   = useRef<number | null>(null);
  const accumulatedS   = useRef(0);
  const enteredFired   = useRef(false);
  const enterTimer     = useRef<ReturnType<typeof setTimeout> | null>(null);
  const heartbeatTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const lastRatio      = useRef(0);

  const stopTimers = useCallback(() => {
    if (enterTimer.current)     { clearTimeout(enterTimer.current);   enterTimer.current = null; }
    if (heartbeatTimer.current) { clearInterval(heartbeatTimer.current); heartbeatTimer.current = null; }
  }, []);

  const startHeartbeat = useCallback(() => {
    if (heartbeatTimer.current) return;
    heartbeatTimer.current = setInterval(() => {
      if (document.visibilityState !== 'visible' || isIdle()) return;
      const additional = visibleSince.current ? (Date.now() - visibleSince.current) / 1000 : 0;
      trackEvent('concept_visible_heartbeat', {
        ...blockMeta,
        seconds_visible: Math.round(accumulatedS.current + additional),
        intersection_ratio: lastRatio.current,
      });
    }, HEARTBEAT_MS);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isIdle, trackEvent]);

  const onEnter = useCallback((ratio: number) => {
    visibleSince.current = Date.now();
    lastRatio.current = ratio;

    if (!enteredFired.current) {
      // Wait for dwell threshold before firing concept_enter_view
      enterTimer.current = setTimeout(() => {
        enteredFired.current = true;
        const additional = visibleSince.current ? (Date.now() - visibleSince.current) / 1000 : 0;
        trackEvent('concept_enter_view', {
          ...blockMeta,
          seconds_visible: Math.round(accumulatedS.current + additional),
        });
        startHeartbeat();
      }, DWELL_THRESHOLD_MS);
    } else {
      startHeartbeat();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [startHeartbeat, trackEvent]);

  const onExit = useCallback(() => {
    stopTimers();

    if (visibleSince.current !== null) {
      accumulatedS.current += (Date.now() - visibleSince.current) / 1000;
      visibleSince.current = null;
    }

    if (enteredFired.current) {
      trackEvent('concept_exit_view', {
        ...blockMeta,
        seconds_visible: Math.round(accumulatedS.current),
      });
      enteredFired.current = false;
      accumulatedS.current = 0;
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stopTimers, trackEvent]);

  useEffect(() => {
    if (process.env.NODE_ENV === 'development' && !blockId) {
      console.warn('TrackedBlock is missing a blockId');
    }
    if (!ref.current) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && entry.intersectionRatio >= VISIBILITY_RATIO) {
          onEnter(entry.intersectionRatio);
        } else {
          onExit();
        }
      },
      { threshold: VISIBILITY_RATIO },
    );

    observer.observe(ref.current);

    return () => {
      observer.disconnect();
      // Flush on unmount
      stopTimers();
      if (visibleSince.current !== null) {
        accumulatedS.current += (Date.now() - visibleSince.current) / 1000;
      }
      if (enteredFired.current) {
        trackEvent('concept_exit_view', {
          ...blockMeta,
          seconds_visible: Math.round(accumulatedS.current),
        });
      }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [blockId]);

  return (
    <div
      ref={ref}
      data-block-id={blockId}
      data-topic={topic}
      data-concept={concept}
      data-content-type={contentType}
      data-label={label}
    >
      {children}
    </div>
  );
}
