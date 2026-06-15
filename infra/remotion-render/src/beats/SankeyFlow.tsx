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

// Sankey simple (una fuente -> varios destinos): una barra origen a la izquierda
// se reparte en cintas cuyo grosor es proporcional al valor, hacia nodos a la
// derecha. Para "a donde se va tu dinero / como se reparte X". Las cintas tienen
// un shimmer que fluye (ese flujo ES el micro-motion).
export type SankeyFlowProps = {
  caption: string;
  source: { label: string; value?: number };
  targets: { label: string; value: number; color?: string }[];
  prefix?: string;
  suffix?: string;
  valueScale?: number;
  valueUnit?: string;
  asPercent?: boolean;
};

const XL = 150; // x de la barra origen
const XLW = 70; // ancho barra origen
const XR = 760; // x donde empiezan los nodos destino
const XRW = 230; // ancho nodo destino
const YTOP = 600;
const YBOT = 1440;
// paleta CATEGORICA on-palette (Filtro A): verde/oro/teal/gris/teal/ambar. SIN rojo
// (rojo = SOLO perdida, regla semantica locked) ni azul/morado (reprueban Filtro A).
const PALETTE = [theme.green, theme.gold, "#5BC0BE", theme.textDim, "#1FA88B", "#E0A93C"];

export const SankeyFlow: React.FC<SankeyFlowProps> = ({
  caption,
  source,
  targets,
  prefix = "$",
  suffix = "",
  valueScale = 1,
  valueUnit = "",
  asPercent = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const total = targets.reduce((a, t) => a + t.value, 0) || 1;
  const H = YBOT - YTOP;
  const GAP = 14;
  const innerH = H - GAP * (targets.length - 1);

  // posicion vertical acumulada en el origen y en cada destino
  let accSrc = YTOP;
  const bands = targets.map((t, i) => {
    const h = (t.value / total) * innerH;
    const srcY0 = accSrc;
    accSrc += h;
    const tgtY0 = YTOP + i * ((innerH / targets.length) + GAP);
    const tgtH = innerH / targets.length;
    return { i, t, h, srcY0, srcY1: srcY0 + h, tgtY0, tgtY1: tgtY0 + tgtH };
  });

  const grow = spring({ frame: frame - 12, fps, config: { damping: 16, mass: 1 } });
  const g = Math.min(grow, 1);
  const capWords = caption.split(" ");

  const fmt = (v: number) => {
    if (asPercent) return Math.round((v / total) * 100) + "%";
    const x = v / valueScale;
    return prefix + x.toLocaleString("en-US", { maximumFractionDigits: x < 10 ? 1 : 0 }) + valueUnit + suffix;
  };

  const ribbon = (b: (typeof bands)[number]) => {
    const x0 = XL + XLW;
    const x1 = XR;
    const xm = (x0 + x1) / 2;
    // ancho de la cinta animado desde 0
    const sy0 = b.srcY0;
    const sy1 = b.srcY0 + (b.srcY1 - b.srcY0) * 1;
    const ty0 = b.tgtY0 + (b.tgtY1 - b.tgtY0) * 0.15;
    const ty1 = b.tgtY1 - (b.tgtY1 - b.tgtY0) * 0.15;
    // interpolacion de apertura: la cinta "crece" en x
    const xEnd = x0 + (x1 - x0) * g;
    const xmA = (x0 + xEnd) / 2;
    return `M ${x0} ${sy0}
            C ${xmA} ${sy0}, ${xmA} ${ty0}, ${xEnd} ${ty0 * g + sy0 * (1 - g)}
            L ${xEnd} ${ty1 * g + sy1 * (1 - g)}
            C ${xmA} ${ty1}, ${xmA} ${sy1}, ${x0} ${sy1} Z`;
  };

  return (
    <StudioScene grid={false} spotlightColor={targets[0]?.color ?? theme.green}>
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
          <defs>
            {bands.map((b) => {
              const color = b.t.color ?? PALETTE[b.i % PALETTE.length];
              return (
                <linearGradient key={b.i} id={`sk${b.i}`} x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor={theme.textDim} stopOpacity={0.45} />
                  <stop offset="100%" stopColor={color} stopOpacity={0.75} />
                </linearGradient>
              );
            })}
          </defs>

          {/* cintas */}
          {bands.map((b) => {
            const color = b.t.color ?? PALETTE[b.i % PALETTE.length];
            // shimmer que fluye a lo largo de la cinta
            const shimmer = 0.6 + 0.4 * Math.sin(frame / 9 - b.i * 0.8);
            return (
              <path
                key={b.i}
                d={ribbon(b)}
                fill={`url(#sk${b.i})`}
                opacity={(0.7 + 0.3 * shimmer) * g}
                style={{ filter: `drop-shadow(0 0 8px ${color}44)` }}
              />
            );
          })}

          {/* barra origen */}
          <rect x={XL} y={YTOP} width={XLW} height={H} rx={14} fill={theme.text} opacity={0.9} />
          <text
            x={XL + XLW / 2}
            y={YTOP - 26}
            textAnchor="middle"
            fill={theme.text}
            fontSize={32}
            fontWeight={800}
            opacity={interpolate(frame, [4, 12], [0, 1], clamp)}
            style={{ fontFamily: theme.font }}
          >
            {source.label}
          </text>
          {source.value != null && (
            <text
              x={XL + XLW / 2}
              y={YBOT + 44}
              textAnchor="middle"
              fill={theme.textDim}
              fontSize={28}
              fontWeight={700}
              opacity={interpolate(frame, [6, 14], [0, 1], clamp)}
              style={{ fontFamily: theme.font, fontVariantNumeric: "tabular-nums" }}
            >
              {fmt(source.value)}
            </text>
          )}

          {/* nodos destino */}
          {bands.map((b) => {
            const color = b.t.color ?? PALETTE[b.i % PALETTE.length];
            const h = b.tgtY1 - b.tgtY0;
            const appear = spring({ frame: frame - (16 + b.i * 5), fps, config: { damping: 16, mass: 0.7 } });
            const a = Math.min(appear, 1);
            return (
              <g key={b.i} opacity={a}>
                <rect x={XR} y={b.tgtY0} width={XRW} height={h} rx={14} fill={color} opacity={0.92} />
                <text x={XR + 24} y={b.tgtY0 + h / 2 - 6} textAnchor="start" fill="#0D1117" fontSize={30} fontWeight={800} style={{ fontFamily: theme.font }}>
                  {b.t.label}
                </text>
                <text x={XR + 24} y={b.tgtY0 + h / 2 + 30} textAnchor="start" fill="#0D1117cc" fontSize={28} fontWeight={700} style={{ fontFamily: theme.font, fontVariantNumeric: "tabular-nums" }}>
                  {fmt(b.t.value)}
                </text>
              </g>
            );
          })}
        </svg>
      </AbsoluteFill>
    </StudioScene>
  );
};
