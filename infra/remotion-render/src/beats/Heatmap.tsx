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

// Heatmap: rejilla de celdas coloreadas por intensidad. Modo diverging (rojo<->
// verde alrededor de 0) para rendimientos +/-, o sequential. Para "rendimiento
// mes a mes" / "que tan caliente esta cada cosa". La celda mas extrema late.
export type HeatmapProps = {
  caption: string;
  rows: { label: string; values: number[] }[];
  colLabels?: string[];
  diverging?: boolean;
  suffix?: string;
  prefix?: string;
  decimals?: number;
};

const X0 = 250;
const X1 = 1010;
const YTOP = 620;
const CELL_GAP = 8;

const mix = (a: string, b: string, t: number) => {
  const pa = [parseInt(a.slice(1, 3), 16), parseInt(a.slice(3, 5), 16), parseInt(a.slice(5, 7), 16)];
  const pb = [parseInt(b.slice(1, 3), 16), parseInt(b.slice(3, 5), 16), parseInt(b.slice(5, 7), 16)];
  const c = pa.map((v, i) => Math.round(v + (pb[i] - v) * t));
  return `rgb(${c[0]},${c[1]},${c[2]})`;
};

export const Heatmap: React.FC<HeatmapProps> = ({
  caption,
  rows,
  colLabels = [],
  diverging = true,
  suffix = "%",
  prefix = "",
  decimals = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const nCols = Math.max(...rows.map((r) => r.values.length));
  const nRows = rows.length;
  const cw = (X1 - X0 - CELL_GAP * (nCols - 1)) / nCols;
  const ch = Math.min(cw, 120);
  const all = rows.flatMap((r) => r.values);
  const absMax = Math.max(...all.map(Math.abs)) || 1;
  const seqMax = Math.max(...all) || 1;
  const seqMin = Math.min(...all);

  // celda mas extrema (para resaltar)
  let hotR = 0,
    hotC = 0,
    hotV = -Infinity;
  rows.forEach((r, ri) =>
    r.values.forEach((v, ci) => {
      if (Math.abs(v) > Math.abs(hotV)) {
        hotV = v;
        hotR = ri;
        hotC = ci;
      }
    })
  );

  const colorOf = (v: number) => {
    const base = "#1B2433";
    if (diverging) {
      const t = Math.min(Math.abs(v) / absMax, 1);
      return mix(base, v >= 0 ? theme.green : theme.red, 0.25 + t * 0.75);
    }
    const t = (v - seqMin) / (seqMax - seqMin || 1);
    return mix(base, theme.green, 0.2 + t * 0.8);
  };

  const fmt = (v: number) =>
    (v > 0 && diverging ? "+" : "") +
    prefix +
    v.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) +
    suffix;

  const pulse = 0.5 + 0.5 * Math.sin(frame / 10);
  const capWords = caption.split(" ");

  return (
    <StudioScene grid={false} spotlightColor={hotV >= 0 ? theme.green : theme.red}>
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
          {/* etiquetas de columna */}
          {colLabels.map((lbl, ci) => (
            <text
              key={ci}
              x={X0 + ci * (cw + CELL_GAP) + cw / 2}
              y={YTOP - 24}
              textAnchor="middle"
              fill={theme.textDim}
              fontSize={26}
              fontWeight={600}
              opacity={interpolate(frame, [6 + ci * 2, 14 + ci * 2], [0, 1], clamp)}
              style={{ fontFamily: theme.font }}
            >
              {lbl}
            </text>
          ))}

          {rows.map((r, ri) => {
            const y = YTOP + ri * (ch + CELL_GAP);
            return (
              <g key={ri}>
                <text x={X0 - 24} y={y + ch / 2 + 10} textAnchor="end" fill={theme.text} fontSize={28} fontWeight={700} opacity={interpolate(frame, [8 + ri * 3, 16 + ri * 3], [0, 1], clamp)} style={{ fontFamily: theme.font }}>
                  {r.label}
                </text>
                {r.values.map((v, ci) => {
                  const x = X0 + ci * (cw + CELL_GAP);
                  const appear = spring({ frame: frame - (10 + (ri + ci) * 4), fps, config: { damping: 16, mass: 0.7 } });
                  const a = Math.min(appear, 1);
                  const isHot = ri === hotR && ci === hotC;
                  return (
                    <g key={ci} opacity={a}>
                      <rect
                        x={x}
                        y={y}
                        width={cw}
                        height={ch}
                        rx={12}
                        fill={colorOf(v)}
                        stroke={isHot ? theme.text : "transparent"}
                        strokeWidth={isHot ? 3 : 0}
                        style={isHot ? { filter: `drop-shadow(0 0 ${8 + pulse * 10}px ${v >= 0 ? theme.green : theme.red})` } : undefined}
                      />
                      <text x={x + cw / 2} y={y + ch / 2 + 9} textAnchor="middle" fill="#FFFFFF" fontSize={Math.min(cw * 0.26, 30)} fontWeight={800} style={{ fontFamily: theme.font, fontVariantNumeric: "tabular-nums" }}>
                        {fmt(v)}
                      </text>
                    </g>
                  );
                })}
              </g>
            );
          })}
        </svg>
      </AbsoluteFill>
    </StudioScene>
  );
};
