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

// Radar / spider: varios ejes y uno o dos poligonos. Para comparar algo en N
// dimensiones (riesgo/rendimiento/liquidez...) o 2 opciones lado a lado. El
// poligono crece desde el centro; los vertices laten.
export type RadarChartProps = {
  caption: string;
  axes: string[];
  series: { label: string; values: number[]; color?: string }[];
  max?: number;
};

const CX = 540;
const CY = 1010;
const R = 360;
const PALETTE = [theme.green, theme.gold];

export const RadarChart: React.FC<RadarChartProps> = ({
  caption,
  axes,
  series,
  max,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const n = axes.length;
  const vMax = max ?? (Math.max(...series.flatMap((s) => s.values)) || 1);
  const angleOf = (i: number) => -Math.PI / 2 + (2 * Math.PI * i) / n;
  const ptOf = (i: number, frac: number) => {
    const a = angleOf(i);
    return [CX + R * frac * Math.cos(a), CY + R * frac * Math.sin(a)] as const;
  };

  const grow = spring({ frame: frame - 12, fps, config: { damping: 15, mass: 1 } });
  const g = Math.min(grow, 1);
  const pulse = 0.5 + 0.5 * Math.sin(frame / 11);
  const capWords = caption.split(" ");

  const rings = [0.25, 0.5, 0.75, 1];

  return (
    <StudioScene grid={false} spotlightColor={series[0]?.color ?? theme.green}>
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
          {/* anillos */}
          {rings.map((rr, i) => (
            <polygon
              key={i}
              points={axes.map((_, k) => ptOf(k, rr).join(",")).join(" ")}
              fill="none"
              stroke="#FFFFFF"
              strokeOpacity={0.1}
              strokeWidth={1.5}
            />
          ))}
          {/* radios */}
          {axes.map((_, k) => {
            const [x, y] = ptOf(k, 1);
            return <line key={k} x1={CX} y1={CY} x2={x} y2={y} stroke="#FFFFFF" strokeOpacity={0.1} strokeWidth={1.5} />;
          })}

          {/* poligonos de cada serie */}
          {series.map((s, si) => {
            const color = s.color ?? PALETTE[si % PALETTE.length];
            const pts = s.values.map((v, k) => ptOf(k, (v / vMax) * g));
            const poly = pts.map((p) => p.join(",")).join(" ");
            return (
              <g key={si}>
                <polygon
                  points={poly}
                  fill={color}
                  fillOpacity={0.18 + (si === 0 ? pulse * 0.06 : 0)}
                  stroke={color}
                  strokeWidth={4}
                  style={{ filter: `drop-shadow(0 0 10px ${color}66)` }}
                />
                {pts.map((p, k) => (
                  <circle key={k} cx={p[0]} cy={p[1]} r={g > 0.95 ? 8 + pulse * 3 : 7} fill={color} />
                ))}
              </g>
            );
          })}

          {/* etiquetas de ejes */}
          {axes.map((lbl, k) => {
            const [x, y] = ptOf(k, 1.16);
            return (
              <text
                key={k}
                x={x}
                y={y + 8}
                textAnchor={Math.abs(x - CX) < 30 ? "middle" : x > CX ? "start" : "end"}
                fill={theme.textDim}
                fontSize={28}
                fontWeight={600}
                opacity={interpolate(frame, [16 + k * 3, 26 + k * 3], [0, 1], clamp)}
                style={{ fontFamily: theme.font }}
              >
                {lbl}
              </text>
            );
          })}
        </svg>

        {/* leyenda */}
        {series.length > 1 && (
          <div style={{ position: "absolute", top: CY + R + 110, width: "100%", display: "flex", justifyContent: "center", gap: 40 }}>
            {series.map((s, si) => {
              const color = s.color ?? PALETTE[si % PALETTE.length];
              return (
                <div key={si} style={{ display: "flex", alignItems: "center", gap: 12, opacity: interpolate(frame, [40 + si * 6, 50 + si * 6], [0, 1], clamp) }}>
                  <div style={{ width: 26, height: 26, borderRadius: 7, background: color }} />
                  <div style={{ fontSize: 32, fontWeight: 700, color: theme.text }}>{s.label}</div>
                </div>
              );
            })}
          </div>
        )}
      </AbsoluteFill>
    </StudioScene>
  );
};
