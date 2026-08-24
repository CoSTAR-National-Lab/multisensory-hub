import React, { useEffect, useRef, useState } from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import styles from './WorkshopParticipantsChart.module.css';
import rawData from '@site/src/data/workshop_participants.json';

// ── Types ─────────────────────────────────────────────────────────────────────

interface BarEntry {
  label: string;
  count: number;
  percent: number;
}

interface PanelData {
  id: string;
  title: string;
  multiSelect?: boolean;
  type?: 'bar' | 'pie';
  bars: BarEntry[];
}

interface StatEntry {
  value: string;
  label: string;
}

interface ParticipantsData {
  stats: StatEntry[];
  caption: string;
  panels: PanelData[];
}

const { stats, caption, panels } = rawData as unknown as ParticipantsData;

// ── SVG layout constants (same coordinate system as LatencyChart) ─────────────

const VIEW_W  = 500;  // viewBox width
const X_START = 235;  // left edge of bar area
const X_END   = 440;  // right edge of bar area (value labels overflow beyond)
const X_RANGE = X_END - X_START;
const BAR_H   = 15;   // bar thickness px
const LINE_H  = 12;   // line-height for multi-line labels
const ROW_PAD = 5;    // vertical padding above/below each bar
const STAGGER = 0.05; // seconds between bar animations

// Bars in a panel are drawn to that panel's own scale (roles and sectors are
// different quantities), so each panel gets its own x-axis.
function panelXMax(bars: BarEntry[]): number {
  const rawMax = Math.max(...bars.map(b => b.percent), 10);
  return Math.ceil(rawMax / 10) * 10;
}

function wrapLabel(text: string, width = 30): string[] {
  const words = text.split(/\s+/);
  const lines: string[] = [];
  let current: string[] = [];
  let currentLen = 0;
  for (const word of words) {
    if (current.length && currentLen + 1 + word.length > width) {
      lines.push(current.join(' '));
      current = [word];
      currentLen = word.length;
    } else {
      current.push(word);
      currentLen += (currentLen ? 1 : 0) + word.length;
    }
  }
  if (current.length) lines.push(current.join(' '));
  return lines;
}

const FONT = 'inherit';  // inherits document font (respects Lexend/system setting)

// ── Panel ─────────────────────────────────────────────────────────────────────

interface PanelProps {
  panel: PanelData;
  colour: string;
  baseDelay: number;
}

function Panel({ panel, colour, baseDelay }: PanelProps) {
  const xMax = panelXMax(panel.bars);
  const xScale = (val: number) => X_START + (val / xMax) * X_RANGE;

  // No x-axis: every bar carries its own value label
  const TOP    = 6;
  const BOTTOM = 6;

  let y = TOP;
  const rows = panel.bars.map((bar, i) => {
    const lines = wrapLabel(bar.label);
    const rh = Math.max(BAR_H, lines.length * LINE_H) + ROW_PAD * 2;
    const yCenter = y + rh / 2;
    y += rh;
    return { bar, lines, yCenter, delay: baseDelay + i * STAGGER };
  });
  const svgH = y + BOTTOM;

  return (
    <svg viewBox={`0 0 ${VIEW_W} ${svgH}`} width="100%"
      style={{ overflow: 'visible', display: 'block' }} aria-hidden="true">

      {rows.map(({ bar, lines, yCenter, delay }, i) => {
        const barW   = bar.percent > 0 ? Math.max(1, xScale(bar.percent) - X_START) : 0;
        const labelX = xScale(bar.percent) + 5;
        const firstLineY = yCenter - ((lines.length - 1) * LINE_H) / 2;

        return (
          <g key={i}>
            {/* Y-axis label (wrapped) */}
            <text textAnchor="end" x={X_START - 6}
              fontSize="0.625em" fontFamily={FONT}
              fill="currentColor" className={styles.dimText}>
              {lines.map((line, li) => (
                <tspan key={li} x={X_START - 6}
                  y={firstLineY + li * LINE_H} dominantBaseline="middle">
                  {line}
                </tspan>
              ))}
            </text>

            {/* Bar */}
            {barW > 0 && (
              <rect
                className={styles.bar}
                x={X_START} y={yCenter - BAR_H / 2}
                width={barW} height={BAR_H}
                fill={colour} rx={2}
                style={{ animationDelay: `${delay}s` } as React.CSSProperties}
              />
            )}

            {/* Value label — percent of respondents */}
            <text
              className={`${styles.valueLabel} ${styles.dimText}`}
              x={labelX} y={yCenter}
              dominantBaseline="middle"
              fontSize="0.625em" fontFamily={FONT}
              fill="currentColor"
              style={{ animationDelay: `${delay + 0.1}s` } as React.CSSProperties}
            >
              {bar.percent}%
            </text>
          </g>
        );
      })}
    </svg>
  );
}

// ── Pie panel ─────────────────────────────────────────────────────────────────

const PIE_W  = 500;
const PIE_H  = 200;
const PIE_CX = PIE_W / 2;
const PIE_CY = PIE_H / 2;  // centred so the group scale-in animates from centre
const PIE_R  = 78;
const SLICE_GAP = 1.5;     // px each slice is nudged outward along its bisector

// θ measured in radians clockwise from 12 o'clock
function piePoint(theta: number, r: number): [number, number] {
  return [PIE_CX + r * Math.sin(theta), PIE_CY - r * Math.cos(theta)];
}

interface PiePanelProps {
  panel: PanelData;
  baseDelay: number;
}

function PiePanel({ panel, baseDelay }: PiePanelProps) {
  const total = panel.bars.reduce((sum, b) => sum + b.percent, 0);
  const sliceFills = [
    'var(--wpc-pie-1)', 'var(--wpc-pie-2)', 'var(--wpc-pie-3)', 'var(--wpc-pie-4)',
  ];

  let angle = 0;
  const slices = panel.bars.map((bar, i) => {
    const sweep = (bar.percent / total) * Math.PI * 2;
    const start = angle;
    const end   = angle + sweep;
    const mid   = (start + end) / 2;
    angle = end;

    const [x0, y0] = piePoint(start, PIE_R);
    const [x1, y1] = piePoint(end, PIE_R);
    const largeArc = sweep > Math.PI ? 1 : 0;
    const path = `M ${PIE_CX} ${PIE_CY} L ${x0} ${y0} A ${PIE_R} ${PIE_R} 0 ${largeArc} 1 ${x1} ${y1} Z`;

    // Nudge the slice outward along its bisector to open a gap
    const dx = SLICE_GAP * Math.sin(mid);
    const dy = -SLICE_GAP * Math.cos(mid);

    // Direct label outside the slice, in text ink
    const [lx, ly] = piePoint(mid, PIE_R + 12);
    const cos = Math.cos(mid);
    const anchor = Math.sin(mid) > 0.1 ? 'start' : (Math.sin(mid) < -0.1 ? 'end' : 'middle');
    const baseline = cos > 0.5 ? 'auto' : (cos < -0.5 ? 'hanging' : 'middle');

    return {
      bar, path, dx, dy, lx, ly, anchor, baseline,
      fill: sliceFills[i % sliceFills.length],
      delay: baseDelay + i * STAGGER * 2,
    };
  });

  return (
    <svg viewBox={`0 0 ${PIE_W} ${PIE_H}`} width="100%"
      style={{ overflow: 'visible', display: 'block' }} aria-hidden="true">
      <g className={styles.pieGroup}
        style={{ animationDelay: `${baseDelay}s` } as React.CSSProperties}>
        {slices.map((s, i) => (
          <path key={i} d={s.path} fill={s.fill}
            transform={`translate(${s.dx} ${s.dy})`}
            className={styles.pieSlice}
            style={{ animationDelay: `${s.delay}s` } as React.CSSProperties} />
        ))}
      </g>
      {slices.map((s, i) => (
        <text key={i}
          className={`${styles.valueLabel} ${styles.dimText}`}
          x={s.lx} y={s.ly}
          textAnchor={s.anchor} dominantBaseline={s.baseline}
          fontSize="0.625em" fontFamily={FONT}
          fill="currentColor"
          style={{ animationDelay: `${s.delay + 0.2}s` } as React.CSSProperties}>
          {s.bar.label} {s.bar.percent}%
        </text>
      ))}
    </svg>
  );
}

// ── Main chart ────────────────────────────────────────────────────────────────

function WorkshopParticipantsChartInner() {
  const wrapperRef = useRef<HTMLElement>(null);
  const [animKey, setAnimKey] = useState(0);

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

  // Per-panel fills via CSS variables so theme/contrast overrides apply
  const panelStyles = [styles.panelRoles, styles.panelSectors, styles.panelExperience];
  const panelFills  = [
    'var(--wpc-roles-fill)',
    'var(--wpc-sectors-fill)',
    'var(--wpc-experience-fill)',
  ];

  // Animation flows top panel → bottom panel
  let cumulative = 0;
  const panelEntries = panels.map((panel, i) => {
    const delay = cumulative;
    cumulative += panel.bars.length * STAGGER;
    return { panel, delay, panelClass: panelStyles[i % panelStyles.length], fill: panelFills[i % panelFills.length] };
  });

  return (
    <figure className={styles.chartWrapper} ref={wrapperRef}
      aria-label="Charts of workshop participants by role, sector and experience level">

      {/* Headline stats */}
      <div className={styles.stats}>
        {stats.map((s, i) => (
          <span key={i} className={styles.stat}>
            <span className={styles.statValue}>{s.value}</span> {s.label}
          </span>
        ))}
      </div>

      <div key={animKey}>
        {panelEntries.map(({ panel, delay, panelClass, fill }) => (
          <div key={panel.id} className={`${styles.panel} ${panelClass}`}>
            <div className={styles.panelTitle}>{panel.title}</div>
            {panel.type === 'pie'
              ? <PiePanel panel={panel} baseDelay={delay} />
              : <Panel panel={panel} colour={fill} baseDelay={delay} />}
          </div>
        ))}
      </div>

      {caption && <figcaption>{caption}</figcaption>}
    </figure>
  );
}

export default function WorkshopParticipantsChart() {
  return (
    <BrowserOnly fallback={<div style={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: 0.5 }}>Loading chart…</div>}>
      {() => <WorkshopParticipantsChartInner />}
    </BrowserOnly>
  );
}
