import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import { StudioScene } from "../studio/StudioScene";

// Cascada: de un valor inicial, sumas/restas encadenadas hasta un total final.
// Barras flotantes (cada una arranca donde acabo la anterior). Verde +, teal −
// (asignacion/gasto rutinario), rojo − SOLO si el paso es loss:true (perdida
// real), oro = totales. Para "de donde sale y a donde va el dinero".
export type WaterfallChartProps = {
  caption: string;
  startLabel: string;
  startValue: number;
  // delta<0 = salida; por defecto teal (asignacion). loss:true lo pinta rojo
  // (perdida real) — el rojo queda reservado estricto a perdida.
  steps: { label: string; delta: number; loss?: boolean }[];
  endLabel: string;
  prefix?: string;
  suffix?: string;
};

const X0 = 120;
const X1 = 960;
const YTOP = 560;
const YBOT = 1480;

export const WaterfallChart: React.FC<WaterfallChartProps> = ({
  caption,
  startLabel,
  startValue,
  steps,
  endLabel,
  prefix = "$",
  suffix = "",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  // columnas: inicio + pasos + fin
  const cols: { label: string; from: number; to: number; kind: "total" | "up" | "down"; loss?: boolean }[] = [];
  let run = startValue;
  cols.push({ label: startLabel, from: 0, to: startValue, kind: "total" });
  for (const st of steps) {
    const from = run;
    run += st.delta;
    cols.push({ label: st.label, from, to: run, kind: st.delta >= 0 ? "up" : "down", loss: st.loss });
  }
  cols.push({ label: endLabel, from: 0, to: run, kind: "total" });

  const peak = Math.max(startValue, run, ...cols.map((c) => Math.max(c.from, c.to))) * 1.12 || 1;
  const yOf = (v: number) => YBOT - (YBOT - YTOP) * (v / peak);
  const n = cols.length;
  const gap = 26;
  const bw = (X1 - X0 - gap * (n - 1)) / n;

  const fmt = (v: number) =>
    prefix + Math.round(v).toLocaleString("en-US") + suffix;

  // oro=totales · verde=+ (ingreso) · teal=salida/asignacion (gasto rutinario, NO
  // es perdida) · rojo=SOLO si el paso es loss:true (perdida real). Mantiene el
  // rojo reservado estricto a perdida (regla locked de color semantico).
  const colorOf = (c: { kind: string; loss?: boolean }) =>
    c.kind === "up"
      ? theme.green
      : c.kind === "total"
      ? theme.gold
      : c.loss
      ? theme.red
      : theme.teal;

  const capWords = caption.split(" ");

  // rojo de escena SOLO si hay perdida real; si no, neutro: verde si el neto sube,
  // teal si baja por asignacion.
  const anyLoss = cols.some((c) => c.loss);
  const sceneColor = anyLoss ? theme.red : run >= startValue ? theme.green : theme.teal;

  return (
    <StudioScene grid spotlightColor={sceneColor}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        <div
          style={{
            position: "absolute",
            top: 250,
            width: "100%",
            textAlign: "center",
            fontSize: 40,
            fontWeight: 500,
            color: theme.textDim,
          }}
        >
          {capWords.map((w, i) => (
            <span key={i} style={{ opacity: interpolate(frame, [2 + i * 3, 8 + i * 3], [0, 1], clamp) }}>
              {w}{" "}
            </span>
          ))}
        </div>

        <svg width="1080" height="1920" style={{ position: "absolute" }}>
          {/* baseline */}
          <line x1={X0 - 10} y1={YBOT} x2={X1 + 10} y2={YBOT} stroke="#FFFFFF" strokeOpacity={0.12} strokeWidth={2} />
          {cols.map((c, i) => {
            const x = X0 + i * (bw + gap);
            const yHi = yOf(Math.max(c.from, c.to));
            const yLo = yOf(Math.min(c.from, c.to));
            const fullH = yLo - yHi;
            const appear = spring({ frame: frame - (10 + i * 12), fps, config: { damping: 14, mass: 0.8 } });
            const h = fullH * Math.min(appear, 1);
            const yTopAnim = c.kind === "total" ? YBOT - h : yLo - h;
            const color = colorOf(c);
            const prevX = X0 + (i - 1) * (bw + gap);
            return (
              <g key={i}>
                {/* conector punteado desde la columna previa */}
                {i > 0 && appear > 0.05 && (
                  <line
                    x1={prevX + bw}
                    y1={yOf(c.from)}
                    x2={x}
                    y2={yOf(c.from)}
                    stroke="#FFFFFF"
                    strokeOpacity={0.3}
                    strokeWidth={2}
                    strokeDasharray="6 8"
                  />
                )}
                <rect
                  x={x}
                  y={yTopAnim}
                  width={bw}
                  height={Math.max(h, 0)}
                  rx={10}
                  fill={color}
                  opacity={c.kind === "total" ? 1 : 0.92}
                  style={{ filter: `drop-shadow(0 0 16px ${color}66)` }}
                />
                {/* valor encima */}
                <text
                  x={x + bw / 2}
                  y={yHi - 22}
                  textAnchor="middle"
                  fill={color}
                  fontSize={34}
                  fontWeight={800}
                  opacity={appear}
                  style={{ fontFamily: theme.font }}
                >
                  {c.kind === "down" ? "−" : c.kind === "up" ? "+" : ""}
                  {fmt(Math.abs(c.kind === "total" ? c.to : c.to - c.from))}
                </text>
                {/* etiqueta abajo */}
                <text
                  x={x + bw / 2}
                  y={YBOT + 46}
                  textAnchor="middle"
                  fill={c.kind === "total" ? theme.text : theme.textDim}
                  fontSize={27}
                  fontWeight={c.kind === "total" ? 800 : 600}
                  opacity={appear}
                  style={{ fontFamily: theme.font }}
                >
                  {c.label}
                </text>
              </g>
            );
          })}
        </svg>
      </AbsoluteFill>
    </StudioScene>
  );
};
