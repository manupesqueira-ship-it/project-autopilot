import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import { StudioScene } from "../studio/StudioScene";

// Lollipop / dumbbell horizontal: filas con tallo + punto(s). Si cada item trae
// value2, se vuelve dumbbell (dos puntos unidos = brecha entre dos grupos/momentos).
// Para "ranking de X" o "brecha entre A y B". Menos pesado visualmente que barras.
export type LollipopChartProps = {
  caption: string;
  items: { label: string; value: number; value2?: number; color?: string }[];
  prefix?: string;
  suffix?: string;
  max?: number;
  highlightIndex?: number;
  legend1?: string;
  legend2?: string;
};

const XLAB = 90;
const X0 = 380;
const X1 = 960;
const YTOP = 660;
const YBOT = 1420;

export const LollipopChart: React.FC<LollipopChartProps> = ({
  caption,
  items,
  prefix = "$",
  suffix = "",
  max,
  highlightIndex = -1,
  legend1,
  legend2,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const isDumbbell = items.some((it) => it.value2 != null);
  const vMax =
    max ??
    (Math.max(...items.flatMap((it) => [it.value, it.value2 ?? 0])) * 1.1 || 1);
  const xOf = (v: number) => X0 + (X1 - X0) * (v / vMax);

  const n = items.length;
  const rowH = (YBOT - YTOP) / n;
  const yOf = (i: number) => YTOP + rowH * (i + 0.5);

  const fmt = (v: number) =>
    prefix + Math.round(v).toLocaleString("en-US") + suffix;

  const pulse = 0.5 + 0.5 * Math.sin(frame / 11);
  const capWords = caption.split(" ");
  const C2 = theme.green; // segundo grupo en dumbbell
  const C1 = theme.gold; // primer grupo

  return (
    <StudioScene grid spotlightColor={isDumbbell ? theme.green : theme.gold}>
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
          {/* eje base */}
          <line x1={X0} y1={YTOP - 20} x2={X0} y2={YBOT - rowH * 0.4} stroke="#FFFFFF" strokeOpacity={0.1} strokeWidth={2} />

          {items.map((it, i) => {
            const y = yOf(i);
            const isHi = i === highlightIndex;
            const baseColor = it.color ?? (isHi ? theme.green : theme.gold);
            const draw = spring({ frame: frame - (12 + i * 9), fps, config: { damping: 16, mass: 0.9 } });
            const d = Math.min(draw, 1);
            const x1v = xOf(it.value) * d + X0 * (1 - d);
            const dotR = 22;

            if (isDumbbell && it.value2 != null) {
              const lower = Math.min(it.value, it.value2);
              const higher = Math.max(it.value, it.value2);
              const xa = xOf(lower);
              const xb = xOf(higher);
              const xbAnim = xa + (xb - xa) * d;
              const lowerColor = it.value <= it.value2 ? C1 : C2;
              const higherColor = it.value <= it.value2 ? C2 : C1;
              return (
                <g key={i}>
                  {/* etiqueta */}
                  <text x={XLAB} y={y + 10} textAnchor="start" fill={theme.text} fontSize={30} fontWeight={700} opacity={Math.min(draw * 2, 1)} style={{ fontFamily: theme.font }}>
                    {it.label}
                  </text>
                  {/* barra de brecha */}
                  <line x1={xa} y1={y} x2={xbAnim} y2={y} stroke="#FFFFFF" strokeOpacity={0.25} strokeWidth={8} strokeLinecap="round" />
                  {/* punto grupo 1 */}
                  <circle cx={xOf(it.value)} cy={y} r={dotR} fill={C1} opacity={Math.min(draw * 1.5, 1)} style={{ filter: `drop-shadow(0 0 8px ${C1}88)` }} />
                  {/* punto grupo 2 */}
                  {d > 0.85 && (
                    <circle cx={xOf(it.value2)} cy={y} r={dotR} fill={C2} style={{ filter: `drop-shadow(0 0 8px ${C2}88)` }} />
                  )}
                  {/* valores SIEMPRE a los extremos (menor a la izq, mayor a la der) */}
                  <text x={xa - 32} y={y + 10} textAnchor="end" fill={lowerColor} fontSize={28} fontWeight={800} opacity={Math.min(draw * 2, 1)} style={{ fontFamily: theme.font, fontVariantNumeric: "tabular-nums" }}>
                    {fmt(lower)}
                  </text>
                  {d > 0.85 && (
                    <text x={xb + 32} y={y + 10} textAnchor="start" fill={higherColor} fontSize={28} fontWeight={800} style={{ fontFamily: theme.font, fontVariantNumeric: "tabular-nums" }}>
                      {fmt(higher)}
                    </text>
                  )}
                </g>
              );
            }

            return (
              <g key={i}>
                <text x={XLAB} y={y + 10} textAnchor="start" fill={isHi ? theme.text : theme.textDim} fontSize={30} fontWeight={isHi ? 800 : 600} opacity={Math.min(draw * 2, 1)} style={{ fontFamily: theme.font }}>
                  {it.label}
                </text>
                {/* tallo */}
                <line x1={X0} y1={y} x2={x1v} y2={y} stroke={baseColor} strokeOpacity={0.5} strokeWidth={8} strokeLinecap="round" />
                {/* punto */}
                <circle
                  cx={x1v}
                  cy={y}
                  r={isHi ? dotR + pulse * 4 : dotR}
                  fill={baseColor}
                  style={{ filter: `drop-shadow(0 0 ${isHi ? 10 + pulse * 10 : 8}px ${baseColor})` }}
                />
                {/* valor */}
                <text x={x1v + dotR + 18} y={y + 10} textAnchor="start" fill={baseColor} fontSize={32} fontWeight={800} opacity={d} style={{ fontFamily: theme.font, fontVariantNumeric: "tabular-nums" }}>
                  {fmt(it.value)}
                </text>
              </g>
            );
          })}
        </svg>

        {/* leyenda dumbbell */}
        {isDumbbell && (legend1 || legend2) && (
          <div
            style={{
              position: "absolute",
              top: YBOT + 30,
              width: "100%",
              display: "flex",
              justifyContent: "center",
              gap: 40,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{ width: 24, height: 24, borderRadius: "50%", background: C1 }} />
              <div style={{ fontSize: 30, fontWeight: 600, color: theme.textDim }}>{legend1}</div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{ width: 24, height: 24, borderRadius: "50%", background: C2 }} />
              <div style={{ fontSize: 30, fontWeight: 600, color: theme.textDim }}>{legend2}</div>
            </div>
          </div>
        )}
      </AbsoluteFill>
    </StudioScene>
  );
};
