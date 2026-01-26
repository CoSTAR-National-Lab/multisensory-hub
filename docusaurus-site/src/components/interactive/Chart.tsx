import React from 'react';
import styles from './Chart.module.css';

interface ChartProps {
  type?: 'bar' | 'line' | 'pie';
  data: { label: string; value: number; color?: string }[];
  title?: string;
  height?: number;
}

const defaultColors = [
  '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e',
  '#f97316', '#eab308', '#22c55e', '#14b8a6',
];

export default function Chart({
  type = 'bar',
  data,
  title,
  height = 300
}: ChartProps) {
  const maxValue = Math.max(...data.map(d => d.value));

  if (type === 'pie') {
    const total = data.reduce((sum, d) => sum + d.value, 0);
    let cumulativePercent = 0;

    const segments = data.map((d, i) => {
      const percent = (d.value / total) * 100;
      const startAngle = cumulativePercent * 3.6;
      cumulativePercent += percent;
      return {
        ...d,
        percent,
        color: d.color || defaultColors[i % defaultColors.length],
        startAngle,
        endAngle: cumulativePercent * 3.6
      };
    });

    return (
      <div className={styles.chartContainer}>
        {title && <h4 className={styles.title}>{title}</h4>}
        <div className={styles.pieWrapper}>
          <div
            className={styles.pie}
            style={{
              background: `conic-gradient(${segments
                .map(s => `${s.color} ${s.startAngle}deg ${s.endAngle}deg`)
                .join(', ')})`
            }}
          />
          <div className={styles.legend}>
            {segments.map((s, i) => (
              <div key={i} className={styles.legendItem}>
                <span
                  className={styles.legendColor}
                  style={{ background: s.color }}
                />
                <span>{s.label}: {s.percent.toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.chartContainer}>
      {title && <h4 className={styles.title}>{title}</h4>}
      <div className={styles.barChart} style={{ height }}>
        <div className={styles.yAxis}>
          {[100, 75, 50, 25, 0].map(tick => (
            <span key={tick} className={styles.yTick}>
              {Math.round(maxValue * tick / 100)}
            </span>
          ))}
        </div>
        <div className={styles.bars}>
          {data.map((d, i) => (
            <div key={i} className={styles.barGroup}>
              <div
                className={styles.bar}
                style={{
                  height: `${(d.value / maxValue) * 100}%`,
                  background: d.color || defaultColors[i % defaultColors.length],
                  animationDelay: `${i * 0.1}s`
                }}
              >
                <span className={styles.barValue}>{d.value}</span>
              </div>
              <span className={styles.barLabel}>{d.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
