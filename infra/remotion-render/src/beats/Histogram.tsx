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

// Histograma: barras pegadas (distribucion / frecuencia), con un marcador
// vertical opcional ("tu estas aqui"). Para "distribucion de sueldos y donde
// caes tu". La barra del marcador se resalta; el resto queda dim.
export type HistogramProps = {
  caption: string;
  bins: number[];
  xLabels?: string[];
  markerIndex?: number;
  markerLabel?: string;
  color?: string;
};

const X0 = 110;
const X1 = 970;
const YTOP = 640;
const YBOT = 1420;

export const Histogram: React.FC<HistogramProps> = ({
  caption,
  bins,
  xLabels = [],
  markerIndex = -1,
  markerLabel = "tú",
  color = theme.green,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const n = bins.length;
  const vMax = Math.max(...bins) * 1.08 || 1;
  const slot = (X1 - X0) / n;
  const bw = slot - 6;
  const yOf = (v: number) => YBOT - (YBOT - YTOP) * (v / vMax);

  const markerX = markerIndex >= 0 ? X0 + slot * (markerIndex + 0.5) : 0;
  const markerPop = spring({ frame: frame - (18 + n * 3), fps, config: { damping: 14, mass: 0.8 } });
  const pulse = 0.5 + 0.5 * Math.sin(frame / 10);
  const capWords = caption.split(" ");

  return (
    <StudioScene grid spotlightColor={color}>
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
          <line x1={X0} y1={YBOT} x2={X1} y2={YBOT} stroke="#FFFFFF" strokeOpacity={0.12} strokeWidth={2} />

          {bins.map((v, i) => {
            const x = X0 + slot * i + 3;
            const yTopFull = yOf(v);
            const fullH = YBOT - yTopFull;
            const grow = spring({ frame: frame - (10 + i * 3), fps, config: { damping: 15, mass: 0.7 } });
            const h = fullH * Math.min(grow, 1);
            const isMark = i === markerIndex;
            const fill = isMark ? color : "#5B6B82";
            return (
              <rect
                key={i}
                x={x}
                y={YBOT - h}
                width={bw}
                height={Math.max(h, 0)}
                rx={6}
                fill={fill}
                opacity={isMark ? 1 : 0.55}
                style={isMark ? { filter: `drop-shadow(0 0 ${10 + pulse * 10}px ${color}aa)` } : undefined}
              />
            );
          })}

          {/* marcador vertical "tu estas aqui" */}
          {markerIndex >= 0 && markerPop > 0.02 && (
            <g opacity={Math.min(markerPop, 1)}>
              <line x1={markerX} y1={YTOP - 70} x2={markerX} y2={YBOT} stroke="#FFFFFF" strokeWidth={3} strokeDasharray="8 8" strokeOpacity={0.8} />
              <polygon
                points={`${markerX - 16},${YTOP - 78} ${markerX + 16},${YTOP - 78} ${markerX},${YTOP - 52}`}
                fill={color}
                style={{ filter: `drop-shadow(0 0 ${8 + pulse * 8}px ${color})` }}
              />
              <text x={markerX} y={YTOP - 92} textAnchor="middle" fill={color} fontSize={40} fontWeight={900} style={{ fontFamily: theme.font }}>
                {markerLabel}
              </text>
            </g>
          )}

          {/* etiquetas x */}
          {xLabels.map((lbl, i) => (
            <text
              key={i}
              x={X0 + slot * (i + 0.5)}
              y={YBOT + 44}
              textAnchor="middle"
              fill={theme.textDim}
              fontSize={24}
              fontWeight={600}
              opacity={interpolate(frame, [22 + i * 2, 32 + i * 2], [0, 1], clamp)}
              style={{ fontFamily: theme.font }}
            >
              {lbl}
            </text>
          ))}
        </svg>
      </AbsoluteFill>
    </StudioScene>
  );
};
