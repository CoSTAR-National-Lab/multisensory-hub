import React, { useCallback, useEffect, useRef, useState } from 'react';
import ReactDOM from 'react-dom';
import BrowserOnly from '@docusaurus/BrowserOnly';
import styles from './LatencyChart.module.css';
import rawData from '@site/src/data/latency_data.json';
import { references, Reference } from '@site/src/data/references';

// ── Types ─────────────────────────────────────────────────────────────────────

interface BarEntry {
  group?: string;
  label: string;
  value: number;
  errorBar: number;
  citations?: number[];
}

interface LatencyData {
  meta: {
    xAxisLabel: string;
    xMax: number;
    toleranceColour: string;
    imperceptibleColour: string;
    legend?: string;
  };
  toleranceBars: BarEntry[];
  imperceptibleBars: BarEntry[];
}

const { meta, toleranceBars, imperceptibleBars } = rawData as unknown as LatencyData;

// ── SVG layout constants ───────────────────────────────────────────────────────

const VIEW_W    = 500;  // viewBox width
const X_START   = 270;  // left edge of bar area
const X_END     = 448;  // right edge of bar area (labels overflow beyond)
const X_RANGE   = X_END - X_START;
const BAR_H     = 15;   // bar thickness px
const LINE_H    = 13;   // line-height for multi-line labels
const ROW_PAD   = 5;    // vertical padding above/below each bar
const STAGGER   = 0.04; // seconds between bar animations

function xScale(val: number): number {
  return X_START + (val / meta.xMax) * X_RANGE;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function getOrderedGroups(bars: BarEntry[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const b of bars) {
    if (b.group && !seen.has(b.group)) { seen.add(b.group); out.push(b.group); }
  }
  return out;
}

function barsForGroup(bars: BarEntry[], group: string): BarEntry[] {
  return [...bars.filter(b => b.group === group)].sort((a, b) => a.value - b.value);
}

function rowHeight(_label: string): number {
  return BAR_H + ROW_PAD * 2;
}

// ── Citation portal popup ─────────────────────────────────────────────────────
// Renders a popup at document.body level (via portal) so it's never clipped
// by SVG boundaries.  Same reference data and UI as RefPopup.

function formatRef(ref: Reference): string {
  const parts: string[] = [];
  if (ref.authors) parts.push(ref.authors);
  if (ref.title)   parts.push(ref.title);
  if (ref.journal) parts.push(ref.journal);
  if (ref.volume)  parts.push(ref.volume);
  if (ref.pages)   parts.push(ref.pages);
  if (ref.year)    parts.push(`(${ref.year})`);
  return parts.filter(Boolean).join('. ').replace(/\.\./g, '.');
}

interface CitationPopupProps {
  refNum: number;
  onClose: () => void;
}

function CitationPopup({ refNum, onClose }: CitationPopupProps) {
  const ref = references.find(r => r.num === refNum);
  const [copied, setCopied] = useState(false);

  const displayText = ref ? formatRef(ref) : `Reference ${refNum}`;
  const doi  = ref?.doi;
  const url  = ref?.url;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(`[${refNum}] ${displayText}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {}
  };

  const handleGoTo = () => {
    window.location.href = `/references#ref-${refNum}`;
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') onClose();
  };

  return ReactDOM.createPortal(
    <>
      {/* full-screen dismiss overlay */}
      <div
        style={{ position: 'fixed', inset: 0, zIndex: 9999 }}
        onClick={onClose}
        aria-hidden="true"
      />
      {/* popup — same style as RefPopup */}
      <div
        role="dialog"
        aria-modal="true"
        onKeyDown={handleKey}
        style={{
          position: 'fixed',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          zIndex: 10000,
          width: 'min(400px, calc(100vw - 32px))',
          background: 'var(--ifm-background-surface-color)',
          border: '1px solid var(--ifm-color-emphasis-300)',
          borderRadius: 8,
          padding: 12,
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          fontSize: '0.875rem',
        }}
      >
        <div style={{ fontWeight: 'bold', color: 'var(--ifm-color-primary)', marginBottom: 6 }}>
          [{refNum}]
        </div>
        {ref ? (
          <div style={{ marginBottom: 12 }}>
            {ref.authors && <div style={{ fontWeight: 500, marginBottom: 4, lineHeight: 1.4 }}>{ref.authors}</div>}
            {ref.title   && <div style={{ marginBottom: 4, lineHeight: 1.4 }}>{ref.title}</div>}
            <div style={{ fontSize: '0.813rem', color: 'var(--ifm-font-color-secondary)', lineHeight: 1.4 }}>
              {ref.journal && <span style={{ fontStyle: 'italic' }}>{ref.journal}</span>}
              {ref.volume  && <span>, {ref.volume}</span>}
              {ref.pages   && <span>: {ref.pages}</span>}
              {ref.year    && <span> ({ref.year})</span>}
            </div>
            {(doi || url) && (
              <div style={{ marginTop: 8, paddingTop: 8, borderTop: '1px dashed var(--ifm-color-emphasis-200)' }}>
                {doi && (
                  <a href={`https://doi.org/${doi}`} target="_blank" rel="noopener noreferrer"
                    style={{ fontSize: '0.75rem', color: 'var(--ifm-color-primary)', wordBreak: 'break-all' }}
                    onClick={e => e.stopPropagation()}>
                    DOI: {doi}
                  </a>
                )}
                {!doi && url && (
                  <a href={url} target="_blank" rel="noopener noreferrer"
                    style={{ fontSize: '0.75rem', color: 'var(--ifm-color-primary)', wordBreak: 'break-all' }}
                    onClick={e => e.stopPropagation()}>
                    {url.length > 50 ? url.slice(0, 50) + '…' : url}
                  </a>
                )}
              </div>
            )}
          </div>
        ) : (
          <div style={{ marginBottom: 12, lineHeight: 1.5 }}>Reference {refNum}</div>
        )}
        <div style={{ display: 'flex', gap: 8, borderTop: '1px solid var(--ifm-color-emphasis-200)', paddingTop: 10 }}>
          {[
            { label: copied ? 'Copied!' : 'Copy', action: handleCopy },
            { label: 'View all', action: handleGoTo },
          ].map(btn => (
            <button key={btn.label} onClick={btn.action}
              style={{
                flex: 1, padding: '6px 12px', cursor: 'pointer',
                background: 'var(--ifm-color-emphasis-100)',
                border: '1px solid var(--ifm-color-emphasis-300)',
                borderRadius: 4, fontSize: '0.813rem',
                color: 'var(--ifm-font-color-base)',
              }}>
              {btn.label}
            </button>
          ))}
        </div>
      </div>
    </>,
    document.body
  );
}

// ── Sub-components ────────────────────────────────────────────────────────────

const FONT = 'inherit';  // inherits document font (respects Lexend/system setting)

interface YLabelProps {
  label: string;
  x: number;
  yCenter: number;
  citations?: number[];
  onCitationClick: (refNum: number) => void;
}

function YLabel({ label, x, yCenter, citations, onCitationClick }: YLabelProps) {
  const singleLine = label.split('\n').join(' ');
  const citStr = citations && citations.length > 0 ? citations.join(',') : null;

  return (
    <g>
      <text textAnchor="end" x={x} y={yCenter} dominantBaseline="middle"
        fontSize="0.625em" fontFamily={FONT}
        fill="currentColor" className={styles.dimText}>
        {singleLine}
      </text>
      {citStr && (
        <text
          textAnchor="end" x={X_START - 2} y={yCenter - 9}
          fontSize="0.5em" fontFamily={FONT}
          fill="var(--ifm-color-primary)"
          className={styles.citationSup}
          style={{ cursor: 'pointer' }}
          onClick={(e) => {
            e.stopPropagation();
            // Open popup for first citation number; multi-citations open first
            onCitationClick(citations![0]);
          }}
          role="button"
          aria-label={`Reference${citations!.length > 1 ? 's' : ''} ${citStr}`}
        >
          {citStr}
        </text>
      )}
    </g>
  );
}

// ── Panel ─────────────────────────────────────────────────────────────────────

interface PanelProps {
  bars: BarEntry[];
  colour: string;
  showXAxis?: boolean;
  baseDelay?: number;
  onCitationClick: (refNum: number) => void;
}

function Panel({ bars, colour, showXAxis = false, baseDelay = 0, onCitationClick }: PanelProps) {
  const sorted = [...bars].sort((a, b) => a.value - b.value);
  const TOP    = 6;
  const BOTTOM = showXAxis ? 34 : 6;

  // Compute y-center for each row
  let y = TOP;
  const rows = sorted.map((bar, i) => {
    const rh = rowHeight(bar.label);
    const yCenter = y + rh / 2;
    y += rh;
    return { bar, yCenter, delay: baseDelay + i * STAGGER };
  });
  const totalH = y;
  const svgH   = totalH + BOTTOM;
  const axisY  = totalH;

  const xTicks = [0, 50, 100, 150, 200, 250].filter(t => t <= meta.xMax);

  return (
    <svg viewBox={`0 0 ${VIEW_W} ${svgH}`} width="100%"
      style={{ overflow: 'visible', display: 'block' }} aria-hidden="true">

      {/* Subtle vertical grid lines */}
      {xTicks.map(tick => (
        <line key={tick} x1={xScale(tick)} x2={xScale(tick)}
          y1={TOP} y2={totalH}
          stroke="currentColor" strokeOpacity={0.07} strokeWidth={1} />
      ))}

      {rows.map(({ bar, yCenter, delay }, i) => {
        const barW   = Math.max(1, xScale(bar.value) - X_START);
        const errPx  = (bar.errorBar / meta.xMax) * X_RANGE;
        const labelX = xScale(bar.value + bar.errorBar) + 5;

        return (
          <g key={i}>
            {/* Y-axis label */}
            <YLabel
              label={bar.label} x={X_START - 6} yCenter={yCenter}
              citations={bar.citations} onCitationClick={onCitationClick}
            />

            {/* Bar */}
            <rect
              className={styles.bar}
              x={X_START} y={yCenter - BAR_H / 2}
              width={barW} height={BAR_H}
              fill={colour} rx={2}
              style={{ animationDelay: `${delay}s` } as React.CSSProperties}
            />

            {/* Error bar — horizontal line, no caps */}
            {bar.errorBar > 0 && (
              <line
                className={styles.errorBar}
                x1={xScale(bar.value) - errPx} x2={xScale(bar.value) + errPx}
                y1={yCenter} y2={yCenter}
                stroke="currentColor" strokeOpacity={0.55} strokeWidth={1.5}
                style={{ animationDelay: `${delay + 0.25}s` } as React.CSSProperties}
              />
            )}

            {/* Value label */}
            <text
              className={`${styles.valueLabel} ${styles.dimText}`}
              x={labelX} y={yCenter}
              dominantBaseline="middle"
              fontSize="0.625em" fontFamily={FONT}
              fill="currentColor"
              style={{ animationDelay: `${delay + 0.1}s` } as React.CSSProperties}
            >
              {bar.value}
            </text>
          </g>
        );
      })}

      {/* X axis — only on bottom panel */}
      {showXAxis && (
        <g>
          <line x1={X_START} x2={X_END} y1={axisY} y2={axisY}
            stroke="currentColor" strokeOpacity={0.25} strokeWidth={1} />
          {xTicks.map(tick => (
            <g key={tick}>
              <line x1={xScale(tick)} x2={xScale(tick)}
                y1={axisY} y2={axisY + 4}
                stroke="currentColor" strokeOpacity={0.4} strokeWidth={1} />
              <text x={xScale(tick)} y={axisY + 14}
                textAnchor="middle" fontSize="0.5625em"
                fill="currentColor" className={styles.dimText}
                fontFamily={FONT}>
                {tick}
              </text>
            </g>
          ))}
          <text x={(X_START + X_END) / 2} y={axisY + 28}
            textAnchor="middle" fontSize="0.625em"
            fill="currentColor" className={styles.dimText}
            fontFamily={FONT}>
            {meta.xAxisLabel}
          </text>
        </g>
      )}
    </svg>
  );
}

// ── Main chart ────────────────────────────────────────────────────────────────

function LatencyChartInner() {
  const wrapperRef = useRef<HTMLElement>(null);
  const [animKey, setAnimKey] = useState(0);
  const [openRef, setOpenRef] = useState<number | null>(null);

  useEffect(() => {
    const el = wrapperRef.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) setAnimKey(k => k + 1);
        }
      },
      { threshold: 0.15 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const handleCitationClick = useCallback((refNum: number) => {
    setOpenRef(refNum);
  }, []);

  const handleClose = useCallback(() => {
    setOpenRef(null);
  }, []);

  const groups = getOrderedGroups(toleranceBars);

  // Precompute per-group start delays so animation flows top-left → bottom-right
  let cumulative = 0;
  const groupEntries = groups.map(group => {
    const bars  = barsForGroup(toleranceBars, group);
    const delay = cumulative;
    cumulative += bars.length * STAGGER;
    return { group, bars, delay };
  });
  const imperceptibleDelay = cumulative;

  // Use CSS variables so dark-mode overrides apply
  const toleranceFill     = 'var(--latency-tolerance-fill)';
  const imperceptibleFill = 'var(--latency-imperceptible-fill)';

  // Pair groups into 2-column rows
  const pairs: [typeof groupEntries[0], typeof groupEntries[0] | null][] = [];
  for (let i = 0; i < groupEntries.length; i += 2) {
    pairs.push([groupEntries[i], groupEntries[i + 1] ?? null]);
  }

  return (
    <figure className={styles.chartWrapper} ref={wrapperRef}>
      {/* Legend */}
      <div className={styles.legend} aria-hidden="true">
        <span>
          <span className={styles.legendSwatch} style={{ background: toleranceFill }} />
          Acceptable
        </span>
        <span>
          <span className={styles.legendSwatch} style={{ background: imperceptibleFill }} />
          Not noticeable
        </span>
      </div>

      {/* 2-column tolerance panels */}
      <div key={animKey} className={styles.panelGrid}>
        {pairs.map(([left, right]) => (
          <React.Fragment key={left.group}>
            <div className={styles.panel}>
              <div className={styles.panelTitle}>{left.group}</div>
              <Panel bars={left.bars} colour={toleranceFill} baseDelay={left.delay}
                onCitationClick={handleCitationClick} />
            </div>
            {right && (
              <div className={styles.panel}>
                <div className={styles.panelTitle}>{right.group}</div>
                <Panel bars={right.bars} colour={toleranceFill} baseDelay={right.delay}
                  onCitationClick={handleCitationClick} />
              </div>
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Full-width imperceptible panel */}
      <div key={`imp-${animKey}`} className={styles.imperceptiblePanel}>
        <div className={styles.panelTitle}>Not noticeable</div>
        <Panel
          bars={imperceptibleBars}
          colour={imperceptibleFill}
          showXAxis
          baseDelay={imperceptibleDelay}
          onCitationClick={handleCitationClick}
        />
      </div>

      {meta.legend && (
        <figcaption>{meta.legend}</figcaption>
      )}

      {/* Citation popup — rendered at document.body via portal, never clipped */}
      {openRef !== null && (
        <CitationPopup refNum={openRef} onClose={handleClose} />
      )}
    </figure>
  );
}

export default function LatencyChart() {
  return (
    <BrowserOnly fallback={<div style={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: 0.5 }}>Loading chart…</div>}>
      {() => <LatencyChartInner />}
    </BrowserOnly>
  );
}
