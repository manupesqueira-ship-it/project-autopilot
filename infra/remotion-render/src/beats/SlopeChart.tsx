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

// Slope chart: dos momentos (izq vs der) y varias lineas que conectan el valor
// antes con el despues. Sube=verde, baja=rojo (semantico). Para "antes vs ahora"
// de varios items a la vez (rendimientos, precios, sueldos).
export type SlopeChartProps = {
  caption: string;
  leftLabel: string;
  rightLabel: string;
  items: { label: string; left: number; right: number; color?: string }[];
  prefix?: string;
  suffix?: string;
  decimals?: number;
};

const XL = 320;
const XR = 760;
const YTOP = 600;
const YBOT = 1360;

export const SlopeChart: React.FC<SlopeChartProps> = ({
  caption,
  leftLabel,
  rightLabel,
  items,
  prefix = "$",
  suffix = "",
  decimals = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const all = items.flatMap((it) => [it.left, it.right]);
  const lo = Math.min(...all);
  const hi = Math.max(...all);
  const pad = (hi - lo) * 0.12 || 1;
  const vMin = lo - pad;
  const vMax = hi + pad;
  const yOf = (v: number) => YBOT - (YBOT - YTOP) * ((v - vMin) / (vMax - vMin));

  const fmt = (v: number) =>
    prefix +
    v.toLocaleString("en-US", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }) +
    suffix;

  const pulse = 0.5 + 0.5 * Math.sin(frame / 11);
  const capWords = caption.split(" ");

  return (
    <StudioScene grid spotlightColor={theme.green}>
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
          {/* ejes verticales */}
          <line x1={XL} y1={YTOP - 20} x2={XL} y2={YBOT + 20} stroke="#FFFFFF" strokeOpacity={0.12} strokeWidth={2} />
          <line x1={XR} y1={YTOP - 20} x2={XR} y2={YBOT + 20} stroke="#FFFFFF" strokeOpacity={0.12} strokeWidth={2} />
          {/* etiquetas de los dos momentos */}
          <text x={XL} y={YTOP - 50} textAnchor="middle" fill={theme.textDim} fontSize={30} fontWeight={700} style={{ fontFamily: theme.font }}>
            {leftLabel}
          </text>
          <text x={XR} y={YTOP - 50} textAnchor="middle" fill={theme.textDim} fontSize={30} fontWeight={700} style={{ fontFamily: theme.font }}>
            {rightLabel}
          </text>

          {items.map((it, i) => {
            const up = it.right >= it.left;
            const color = it.color ?? (up ? theme.green : theme.red);
            const yl = yOf(it.left);
            const yr = yOf(it.right);
            const draw = spring({ frame: frame - (14 + i * 8), fps, config: { damping: 16, mass: 0.9 } });
            const d = Math.min(draw, 1);
            const xNow = XL + (XR - XL) * d;
            const yNow = yl + (yr - yl) * d;
            const dotR = 13;
            return (
              <g key={i}>
                <line
                  x1={XL}
                  y1={yl}
                  x2={xNow}
                  y2={yNow}
                  stroke={color}
                  strokeWidth={6}
                  strokeLinecap="round"
                  opacity={0.95}
                  style={{ filter: `drop-shadow(0 0 8px ${color}66)` }}
                />
                {/* punto izquierdo */}
                <circle cx={XL} cy={yl} r={dotR} fill={color} opacity={Math.min(draw * 2, 1)} />
                {/* punto derecho aparece al terminar el trazo, late */}
                {d > 0.98 && (
                  <circle
                    cx={XR}
                    cy={yr}
                    r={dotR + pulse * 3}
                    fill={color}
                    style={{ filter: `drop-shadow(0 0 ${8 + pulse * 8}px ${color})` }}
                  />
                )}
                {/* valores en ambos extremos */}
                <text x={XL - 28} y={yl + 10} textAnchor="end" fill={color} fontSize={32} fontWeight={800} opacity={Math.min(draw * 2, 1)} style={{ fontFamily: theme.font, fontVariantNumeric: "tabular-nums" }}>
                  {fmt(it.left)}
                </text>
                {d > 0.9 && (
                  <text x={XR + 28} y={yr + 10} textAnchor="start" fill={color} fontSize={36} fontWeight={900} style={{ fontFamily: theme.font, fontVariantNumeric: "tabular-nums" }}>
                    {fmt(it.right)}
                  </text>
                )}
                {/* etiqueta del item junto al punto derecho, mas chica y dim */}
                {d > 0.95 && (
                  <text x={XR + 28} y={yr + 44} textAnchor="start" fill={theme.textDim} fontSize={26} fontWeight={600} style={{ fontFamily: theme.font }}>
                    {it.label}
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </AbsoluteFill>
    </StudioScene>
  );
};
