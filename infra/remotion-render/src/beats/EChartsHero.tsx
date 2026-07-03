import React, { useEffect, useRef, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import * as echarts from "echarts";

// EChartsHero — POC: renderiza gráficas de la librería PRO Apache ECharts dentro de Remotion,
// con NUESTROS datos y estilo editorial. Prueba de un look serio/premium (no caricatura),
// parametrizable con cifras exactas. variant = area | bars | gauge.

const FONT = "InterVar, Inter, Helvetica, sans-serif";

export type EChartsHeroProps = {
  variant?: "area" | "bars" | "gauge";
  theme?: "light" | "dark";
  kicker?: string;
  label?: string;
  caption?: string;
};

export const EChartsHero: React.FC<EChartsHeroProps> = ({
  variant = "area",
  theme = "light",
  kicker = "40 AÑOS INVIRTIENDO",
  label = "Tu dinero crece",
  caption = "Apache ECharts · renderizado en Remotion",
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const dark = theme === "dark";
  const INK = dark ? "#F3EFE7" : "#1B1712";
  const PAPER = dark ? "#0A0B0D" : "#F1ECE1";
  const ACCENT = "#9E2B22";
  const GREEN = dark ? "#43B980" : "#1F7A4D";
  const MUTE = dark ? "#8A909B" : "#7A7264";
  const HAIR = dark ? "#2B2F38" : "#CDC4B2";

  const ref = useRef<HTMLDivElement>(null);
  const chartRef = useRef<echarts.ECharts | null>(null);
  const [handle] = useState(() => delayRender("echarts init"));

  useEffect(() => {
    if (ref.current && !chartRef.current) {
      chartRef.current = echarts.init(ref.current, null, { renderer: "svg", width: 1080, height: 1000 });
      continueRender(handle);
    }
    return () => { chartRef.current?.dispose(); chartRef.current = null; };
  }, [handle]);

  useEffect(() => {
    const chart = chartRef.current;
    if (!chart) return;
    const prog = interpolate(frame, [8, durationInFrames - 24], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const eased = 1 - Math.pow(1 - prog, 3);
    const col = variant === "bars" ? INK : GREEN;

    let option: echarts.EChartsCoreOption;
    if (variant === "area") {
      const full = [8, 11, 15, 21, 30, 43, 63, 95, 140, 200];
      const k = eased * (full.length - 1);
      const shown = full.map((v, i) => (i <= Math.floor(k) ? v : i === Math.floor(k) + 1 ? full[Math.floor(k)] + (v - full[Math.floor(k)]) * (k - Math.floor(k)) : null));
      option = {
        backgroundColor: "transparent",
        grid: { left: 70, right: 70, top: 40, bottom: 70 },
        xAxis: { type: "category", boundaryGap: false, data: full.map((_, i) => `A${i}`), axisLine: { lineStyle: { color: HAIR } }, axisTick: { show: false }, axisLabel: { show: false } },
        yAxis: { type: "value", max: 210, show: false },
        series: [{
          type: "line", smooth: true, symbol: "none", data: shown, connectNulls: false,
          lineStyle: { color: GREEN, width: 8, shadowColor: GREEN, shadowBlur: 22 },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: dark ? "rgba(67,185,128,0.45)" : "rgba(31,122,77,0.34)" }, { offset: 1, color: "rgba(0,0,0,0)" }]) },
        }],
        animation: false,
      };
    } else if (variant === "bars") {
      const cats = ["A los 25", "A los 35", "A los 45"];
      const vals = [6982016, 2980719, 1210000].map((v) => Math.round(v * eased));
      option = {
        backgroundColor: "transparent",
        grid: { left: 70, right: 90, top: 40, bottom: 90 },
        xAxis: { type: "category", data: cats, axisLine: { lineStyle: { color: HAIR } }, axisTick: { show: false }, axisLabel: { color: MUTE, fontSize: 34, fontFamily: FONT } },
        yAxis: { type: "value", max: 7200000, show: false },
        series: [{
          type: "bar", data: vals.map((v, i) => ({ value: v, itemStyle: { color: i === 0 ? GREEN : INK, borderRadius: [12, 12, 0, 0] } })), barWidth: 150,
          label: { show: true, position: "top", color: INK, fontSize: 40, fontWeight: "bold", fontFamily: FONT, formatter: (p: { value: number }) => "$" + (p.value / 1e6).toFixed(1) + "M" },
        }],
        animation: false,
      };
    } else {
      option = {
        backgroundColor: "transparent",
        series: [{
          type: "gauge", startAngle: 200, endAngle: -20, min: 0, max: 100, radius: "82%", center: ["50%", "58%"],
          progress: { show: true, width: 34, itemStyle: { color: GREEN } },
          axisLine: { lineStyle: { width: 34, color: [[1, HAIR]] } },
          pointer: { itemStyle: { color: INK }, width: 8, length: "62%" },
          axisTick: { show: false }, splitLine: { show: false }, axisLabel: { show: false },
          anchor: { show: true, size: 26, itemStyle: { color: INK } },
          detail: { valueAnimation: false, fontSize: 130, fontWeight: "bolder", color: INK, fontFamily: FONT, offsetCenter: [0, "12%"], formatter: "{value}" },
          data: [{ value: Math.round(68 * eased) }],
        }],
        animation: false,
      };
    }
    chart.setOption(option, true);
  });

  return (
    <AbsoluteFill style={{ backgroundColor: PAPER, fontFamily: FONT, color: INK }}>
      {dark && <div style={{ position: "absolute", left: 0, top: 380, width: 1080, height: 1080, borderRadius: "50%", background: "radial-gradient(circle at 40% 40%, #34507E3D 0%, transparent 62%)" }} />}
      <div style={{ position: "absolute", top: 78, left: 96, fontSize: 27, fontWeight: 700, letterSpacing: "0.28em", color: INK }}>DINERO&nbsp;IA</div>
      <div style={{ position: "absolute", top: 130, left: 96, width: 888, height: dark ? 1 : 2, background: dark ? "#2B2F38" : INK }} />
      {kicker && <div style={{ position: "absolute", top: 250, left: 96, fontSize: 30, fontWeight: 700, letterSpacing: "0.2em", color: ACCENT }}>{kicker}</div>}
      {label && <div style={{ position: "absolute", top: 320, left: 96, right: 96, fontSize: 66, fontWeight: 800, lineHeight: 1.04, letterSpacing: "-0.02em", color: INK }}>{label}</div>}
      <div ref={ref} style={{ position: "absolute", top: 560, left: 0, width: 1080, height: 1000 }} />
      {caption && <div style={{ position: "absolute", bottom: 130, left: 96, right: 96, fontSize: 32, fontWeight: 400, color: MUTE }}>{caption}</div>}
    </AbsoluteFill>
  );
};
