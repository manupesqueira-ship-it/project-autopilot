import * as echarts from "echarts";
import React, { useEffect, useRef, useState } from "react";
import { continueRender, delayRender } from "remotion";
import { L } from "./look";

// ============================================================================
// CHARTS KIT — Apache ECharts (renderer svg) como MOTOR de gráficas de datos
// del look A. Implementa los patrones premium de MINED_KNOWLEDGE_2026-07-03:
// línea héroe glow 3 capas · área a transparente · barras gradiente + label
// directo · multi-línea endLabel + markLine · gauge arco fino · donut ultrafino
// · racing bars. Reglas duras aquí dentro (checklist anti-look-de-librería):
//   - animation:false SIEMPRE; TODO movimiento entra por `progress` (por frame).
//   - ejes/ticks OFF, máx 3 splitLines a rgba(255,255,255,.05), direct labels.
//   - legend/tooltip/toolbox OFF. UN acento por escena; el resto lecho neutro.
//   - backgroundColor transparente (el fondo lo pone LiveBg).
//   - yAxis min/max SIEMPRE fijos (si no, la escena tiembla en el draw-on).
// Los beats (ChartBeats2) ponen kicker/caption/timing; aquí NO hay tiempo propio.
// ============================================================================

// lecho neutro (escalera de grises fríos sobre #08090B, NO semánticos)
export const RAIL = "#1B1E23";
export const GHOST = "#23262C";
export const LADDER = ["#2A2E35", "#22252B", "#1B1E23"] as const;
export const SPLIT = "rgba(255,255,255,0.05)";
export const COOL = ["#3E5C76", "#5A6B7B"] as const; // líneas secundarias

export const hexA = (hex: string, a: number) => {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
};

// formatter compacto es-MX para ejes/labels ($ opcional lo pone el beat)
export const compact = (v: number): string => {
  const abs = Math.abs(v);
  if (abs >= 1e12) return (v / 1e12).toFixed(abs >= 1e13 ? 0 : 1) + " B"; // billones es-MX
  if (abs >= 1e9) return (v / 1e9).toFixed(abs >= 1e10 ? 0 : 1) + " mil M";
  if (abs >= 1e6) return (v / 1e6).toFixed(abs >= 1e7 ? 0 : 1) + " M";
  if (abs >= 1e3) return (v / 1e3).toFixed(abs >= 1e4 ? 0 : 1) + "k";
  return String(Math.round(v * 10) / 10);
};

// ── Lienzo ECharts dentro de Remotion ───────────────────────────────────────
// init una vez (svg, delayRender) + setOption en CADA render (frame nuevo).
export const EChartCanvas: React.FC<{
  option: echarts.EChartsCoreOption;
  width?: number;
  height?: number;
  style?: React.CSSProperties;
}> = ({ option, width = 1080, height = 1050, style }) => {
  const ref = useRef<HTMLDivElement>(null);
  const chartRef = useRef<echarts.ECharts | null>(null);
  const [handle] = useState(() => delayRender("echarts init"));
  useEffect(() => {
    if (ref.current && !chartRef.current) {
      chartRef.current = echarts.init(ref.current, null, { renderer: "svg", width, height });
      continueRender(handle);
    }
    return () => {
      chartRef.current?.dispose();
      chartRef.current = null;
    };
  }, [handle, width, height]);
  useEffect(() => {
    chartRef.current?.setOption(option, true);
  });
  return <div ref={ref} style={{ width, height, ...style }} />;
};

// ── fragmentos base (checklist) ─────────────────────────────────────────────
export const gridAir = { left: "9%", right: "13%", top: "10%", bottom: "12%" };

const catAxis = (labels: string[], show = true) => ({
  type: "category" as const,
  boundaryGap: false,
  data: labels,
  axisLine: { show: false },
  axisTick: { show: false },
  axisLabel: show
    ? { color: L.mute, fontSize: 26, fontFamily: L.font, interval: "auto" as const }
    : { show: false },
});

const valAxis = (min: number, max: number, show = false) => ({
  type: "value" as const,
  min,
  max,
  axisLine: { show: false },
  axisTick: { show: false },
  axisLabel: show
    ? { color: L.mute, fontSize: 22, fontFamily: L.font, formatter: (v: number) => compact(v) }
    : { show: false },
  splitLine: show ? { show: true, lineStyle: { color: SPLIT } } : { show: false },
  splitNumber: 3,
});

// slice de draw-on: datos visibles hasta progress, con punto interpolado en la
// cabeza. TRUNCADO (no null-padding): visualMap/endLabel de ECharts truenan con
// nulls ("Cannot read properties of undefined (reading 'coord')"). El eje queda
// fijo porque el xAxis lleva SIEMPRE los labels completos.
const drawOn = (data: number[], progress: number): number[] => {
  const n = data.length;
  const k = Math.min(Math.max(progress, 0), 1) * (n - 1);
  const lo = Math.floor(k);
  if (lo >= n - 1) return data.slice();
  const head = data[lo] + (data[lo + 1] - data[lo]) * (k - lo);
  return [...data.slice(0, lo + 1), head];
};

// posición de la cabeza del trazo en % del ancho (para overlays del beat)
export const headFrac = (progress: number) => Math.min(Math.max(progress, 0), 1);

// límites "bonitos" para ejes (pasos 1/2/5×10^n): evita labels tipo "6.8"/"143"
const niceStep = (span: number) => {
  const raw = span / 3;
  const mag = 10 ** Math.floor(Math.log10(Math.max(raw, 1e-9)));
  const norm = raw / mag;
  return (norm <= 1 ? 1 : norm <= 2 ? 2 : norm <= 5 ? 5 : 10) * mag;
};
export const niceBounds = (min: number, max: number): [number, number] => {
  if (max - min < 1e-9) return [min - 1, max + 1];
  const step = niceStep(max - min);
  return [Math.floor(min / step) * step, Math.ceil(max / step) * step];
};

// ── 1. LÍNEA HÉROE — glow 3 capas + área opcional + umbral semántico ───────
export const lineHeroOption = (cfg: {
  data: number[];
  progress: number; // 0..1
  color?: string;
  xLabels?: string[];
  yMin?: number;
  yMax?: number;
  area?: boolean;
  threshold?: number; // visualMap: L.red debajo / color arriba (pérdida/ganancia)
  showAxis?: boolean;
}): echarts.EChartsCoreOption => {
  const c = cfg.color ?? L.green;
  const shown = drawOn(cfg.data, cfg.progress);
  // el umbral entra al envolvente para que SIEMPRE quede dentro del eje
  const env = cfg.threshold != null ? [...cfg.data, cfg.threshold] : cfg.data;
  const span = Math.max(...env) - Math.min(...env);
  const [nMin, nMax] = niceBounds(Math.min(...env) - span * 0.06, Math.max(...env) + span * 0.08);
  const yMin = cfg.yMin ?? nMin;
  const yMax = cfg.yMax ?? nMax;
  // con threshold el color lo pinta el visualMap: NO fijar lineStyle.color
  // (un color explícito lo anula y la línea sale de un solo color)
  const layer = (width: number, opacity: number, extra: Record<string, unknown> = {}) => ({
    type: "line" as const,
    smooth: 0.3,
    showSymbol: false,
    silent: true,
    data: shown,
    connectNulls: false,
    lineStyle: { width, ...(cfg.threshold == null ? { color: c } : {}), opacity, ...extra },
    z: 5,
  });
  return {
    backgroundColor: "transparent",
    grid: gridAir,
    xAxis: catAxis(cfg.xLabels ?? cfg.data.map((_, i) => String(i)), cfg.showAxis ?? false),
    yAxis: valAxis(yMin, yMax, cfg.showAxis ?? false),
    ...(cfg.threshold != null
      ? {
          // continuo (NO piecewise: bug 'coord' con línea smooth). Rampa de 24
          // pasos con el corte rojo→acento EXACTO en el umbral (los 3 colores
          // espaciados uniformes dejaban el tramo perdedor gris, no rojo).
          visualMap: [
            {
              show: false,
              type: "continuous" as const,
              seriesIndex: [0, 1, 2],
              min: Math.min(...cfg.data),
              max: Math.max(...cfg.data),
              inRange: {
                color: Array.from({ length: 24 }, (_, i) =>
                  i / 23 <
                  (cfg.threshold! - Math.min(...cfg.data)) /
                    Math.max(Math.max(...cfg.data) - Math.min(...cfg.data), 1e-9)
                    ? L.red
                    : c,
                ),
              },
            },
          ],
        }
      : {}),
    series: [
      layer(25, 0.07), // halo
      layer(11, 0.22), // medio
      {
        ...layer(4.5, 1, { shadowBlur: 16, shadowColor: hexA(c, 0.45) }),
        ...(cfg.area
          ? {
              areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: hexA(c, 0.3) },
                  { offset: 1, color: hexA(c, 0) },
                ]),
              },
            }
          : {}),
      },
    ],
    animation: false,
  };
};

// ── 2. BARRAS PREMIUM — gradiente + borde redondo + label directo arriba ────
export const barsOption = (cfg: {
  cats: string[];
  values: number[];
  progress: number | number[]; // uno global o por barra (stagger)
  accentIndex?: number; // UN acento: la barra del sujeto; resto GHOST
  accent?: string;
  labelFmt?: (v: number) => string;
  yMax?: number;
}): echarts.EChartsCoreOption => {
  const acc = cfg.accent ?? L.green;
  const fmt = cfg.labelFmt ?? compact;
  const p = (i: number) =>
    Array.isArray(cfg.progress) ? (cfg.progress[i] ?? 0) : cfg.progress;
  const yMax = cfg.yMax ?? Math.max(...cfg.values) * 1.18;
  return {
    backgroundColor: "transparent",
    grid: { ...gridAir, top: "16%", bottom: "10%" },
    xAxis: {
      ...catAxis(cfg.cats, true),
      boundaryGap: true,
      axisLabel: { color: L.mute, fontSize: 30, fontWeight: 600, fontFamily: L.font },
    },
    yAxis: valAxis(0, yMax, false),
    series: [
      {
        type: "bar",
        silent: true,
        barWidth: "42%",
        data: cfg.values.map((v, i) => {
          const isAcc = i === (cfg.accentIndex ?? 0);
          return {
            value: Math.round(v * p(i)),
            itemStyle: {
              borderRadius: [10, 10, 0, 0],
              color: isAcc
                ? new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: acc },
                    { offset: 1, color: hexA(acc, 0.25) },
                  ])
                : GHOST,
              ...(isAcc ? { shadowBlur: 24, shadowColor: hexA(acc, 0.35) } : {}),
            },
            label: {
              show: p(i) > 0.05,
              position: "top" as const,
              fontWeight: 800,
              fontSize: 40,
              fontFamily: L.font,
              color: isAcc ? L.ink : L.mute,
              formatter: (par: { value: number }) => fmt(par.value),
            },
          };
        }),
      },
    ],
    animation: false,
  };
};

// ── 3. MULTI-LÍNEA — endLabel nombre+valor + markLine de umbral ─────────────
export const multiLineOption = (cfg: {
  series: { name: string; data: number[]; color?: string }[]; // máx 3; [0] = protagonista
  progress: number;
  xLabels?: string[];
  yMin?: number;
  yMax?: number;
  threshold?: number;
  thresholdLabel?: string;
  endFmt?: (v: number) => string;
  accent?: string;
}): echarts.EChartsCoreOption => {
  const acc = cfg.accent ?? L.green;
  const fmt = cfg.endFmt ?? compact;
  const all = cfg.series.flatMap((s) => s.data);
  const env = cfg.threshold != null ? [...all, cfg.threshold] : all;
  const span = Math.max(...env) - Math.min(...env);
  const [nMin, nMax] = niceBounds(Math.min(...env) - span * 0.06, Math.max(...env) + span * 0.08);
  const yMin = cfg.yMin ?? nMin;
  const yMax = cfg.yMax ?? nMax;
  const n = Math.max(...cfg.series.map((s) => s.data.length));
  return {
    backgroundColor: "transparent",
    grid: { ...gridAir, right: "24%" }, // aire para endLabel nombre+valor (no cortar)
    xAxis: catAxis(cfg.xLabels ?? Array.from({ length: n }, (_, i) => String(i)), true),
    yAxis: valAxis(yMin, yMax, true),
    series: cfg.series.slice(0, 3).map((s, i) => {
      const isHero = i === 0;
      const color = s.color ?? (isHero ? acc : COOL[i - 1] ?? COOL[1]);
      return {
        type: "line" as const,
        name: s.name,
        smooth: 0.3,
        showSymbol: false,
        silent: true,
        data: drawOn(s.data, cfg.progress),
        connectNulls: false,
        lineStyle: {
          width: isHero ? 4.5 : 2.5,
          color,
          ...(isHero ? { shadowBlur: 14, shadowColor: hexA(color, 0.45) } : {}),
        },
        endLabel: {
          show: cfg.progress > 0.97,
          formatter: (p: { seriesName: string; value: number }) =>
            `${p.seriesName}  ${fmt(p.value as number)}`,
          fontWeight: isHero ? 800 : 600,
          fontSize: isHero ? 30 : 24,
          fontFamily: L.font,
          color: isHero ? color : L.mute,
          distance: 12,
        },
        labelLayout: { moveOverlap: "shiftY" as const },
        ...(isHero && cfg.threshold != null
          ? {
              markLine: {
                silent: true,
                symbol: "none",
                lineStyle: { type: "dashed" as const, color: "rgba(255,255,255,0.25)", width: 2 },
                label: {
                  formatter: cfg.thresholdLabel ?? "",
                  color: L.mute,
                  fontSize: 24,
                  fontFamily: L.font,
                  position: "insideEndTop" as const,
                },
                data: [{ yAxis: cfg.threshold }],
              },
            }
          : {}),
      };
    }),
    animation: false,
  };
};

// ── 4. GAUGE ARCO FINO — un porcentaje protagonista ─────────────────────────
export const gaugeOption = (cfg: {
  value: number; // valor final (ej. 68)
  progress: number;
  max?: number;
  color?: string;
  fmt?: (v: number) => string;
}): echarts.EChartsCoreOption => {
  const c = cfg.color ?? L.green;
  const fmt = cfg.fmt ?? ((v: number) => `${Math.round(v)}%`);
  const shown = cfg.value * Math.min(Math.max(cfg.progress, 0), 1);
  return {
    backgroundColor: "transparent",
    series: [
      {
        type: "gauge",
        silent: true,
        startAngle: 210,
        endAngle: -30,
        min: 0,
        max: cfg.max ?? 100,
        radius: "78%",
        center: ["50%", "56%"],
        pointer: { show: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        axisLine: { lineStyle: { width: 16, color: [[1, RAIL]] } },
        progress: {
          show: true,
          width: 16,
          roundCap: true,
          itemStyle: { color: c, shadowBlur: 20, shadowColor: hexA(c, 0.5) },
        },
        detail: {
          valueAnimation: false,
          offsetCenter: [0, "-4%"],
          fontSize: 130,
          fontWeight: 800,
          fontFamily: L.font,
          color: L.ink,
          formatter: (v: number) => fmt(v),
        },
        data: [{ value: shown }],
      },
    ],
    animation: false,
  };
};

// ── 5. DONUT ULTRAFINO — proporción con protagonista; cifra central la pone
//      el beat como capa React encima (NUNCA texto del chart) ────────────────
export const donutOption = (cfg: {
  parts: { name: string; value: number }[]; // [0] = protagonista
  progress: number;
  accent?: string;
}): echarts.EChartsCoreOption => {
  const acc = cfg.accent ?? L.green;
  const total = cfg.parts.reduce((a, b) => a + b.value, 0);
  const p = Math.min(Math.max(cfg.progress, 0), 1);
  const data: Record<string, unknown>[] = cfg.parts.map((part, i) => ({
    name: part.name,
    value: part.value * p,
    itemStyle: {
      color: i === 0 ? acc : LADDER[(i - 1) % LADDER.length],
      borderRadius: 8,
      borderColor: L.bg,
      borderWidth: 3,
      ...(i === 0 ? { shadowBlur: 16, shadowColor: hexA(acc, 0.5) } : {}),
    },
  }));
  if (p < 1) {
    // barrido: el hueco restante gira cerrado conforme progresa
    data.push({
      name: "_rest",
      value: total * (1 - p),
      itemStyle: { color: "transparent", borderWidth: 0 },
      emphasis: { disabled: true },
    });
  }
  return {
    backgroundColor: "transparent",
    series: [
      {
        type: "pie",
        silent: true,
        radius: ["74%", "86%"],
        center: ["50%", "50%"],
        padAngle: 2,
        label: { show: false },
        labelLine: { show: false },
        data,
      },
    ],
    animation: false,
  };
};

// ── 6. RACING BARS — carrera entre keyframes, orden vivo ────────────────────
export const raceOption = (cfg: {
  steps: { period: string; values: Record<string, number> }[];
  t: number; // 0..1 sobre TODOS los pasos
  accentName: string;
  fmt?: (v: number) => string;
  maxBars?: number;
}): { option: echarts.EChartsCoreOption; period: string } => {
  const fmt = cfg.fmt ?? compact;
  const maxBars = cfg.maxBars ?? 7;
  const t = Math.min(Math.max(cfg.t, 0), 1) * (cfg.steps.length - 1);
  const lo = Math.floor(t);
  const hi = Math.min(lo + 1, cfg.steps.length - 1);
  const f = t - lo;
  const names = Object.keys(cfg.steps[0].values);
  const vals = names
    .map((name) => ({
      name,
      value:
        (cfg.steps[lo].values[name] ?? 0) +
        ((cfg.steps[hi].values[name] ?? 0) - (cfg.steps[lo].values[name] ?? 0)) * f,
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, maxBars);
  const maxV = Math.max(...cfg.steps.flatMap((s) => Object.values(s.values)));
  return {
    period: cfg.steps[Math.round(t)].period,
    option: {
      backgroundColor: "transparent",
      grid: { left: "26%", right: "18%", top: "6%", bottom: "6%" },
      xAxis: { type: "value", max: maxV * 1.05, show: false },
      yAxis: {
        type: "category",
        inverse: true,
        data: vals.map((v) => v.name),
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: L.mute, fontSize: 28, fontWeight: 600, fontFamily: L.font },
      },
      series: [
        {
          type: "bar",
          silent: true,
          barWidth: "58%",
          data: vals.map((v) => ({
            value: v.value,
            itemStyle: {
              borderRadius: [0, 8, 8, 0],
              color:
                v.name === cfg.accentName
                  ? new echarts.graphic.LinearGradient(1, 0, 0, 0, [
                      { offset: 0, color: L.green },
                      { offset: 1, color: hexA(L.green, 0.35) },
                    ])
                  : GHOST,
              ...(v.name === cfg.accentName
                ? { shadowBlur: 18, shadowColor: hexA(L.green, 0.35) }
                : {}),
            },
            label: {
              show: true,
              position: "right" as const,
              fontWeight: 800,
              fontSize: 30,
              fontFamily: L.font,
              color: v.name === cfg.accentName ? L.ink : L.mute,
              formatter: (p: { value: number }) => fmt(p.value),
            },
          })),
        },
      ],
      animation: false,
    },
  };
};
