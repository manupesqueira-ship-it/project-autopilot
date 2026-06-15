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

// Velas OHLC: mecha (high-low) + cuerpo (open-close). Verde si cierra arriba,
// rojo si cierra abajo. Barren de izquierda a derecha; al final marca el cierre
// con guia punteada + lectura de precio y % total. Para "como se movio X".
export type CandlestickChartProps = {
  caption: string;
  candles: { o: number; h: number; l: number; c: number }[];
  prefix?: string;
  suffix?: string;
  readoutLabel?: string;
  highlightLast?: boolean;
};

const X0 = 130;
const X1 = 950;
const YTOP = 640;
const YBOT = 1440;

export const CandlestickChart: React.FC<CandlestickChartProps> = ({
  caption,
  candles,
  prefix = "$",
  suffix = "",
  readoutLabel = "cierre",
  highlightLast = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const n = candles.length;
  const lo = Math.min(...candles.map((c) => c.l));
  const hi = Math.max(...candles.map((c) => c.h));
  const padv = (hi - lo) * 0.08 || 1;
  const pMin = lo - padv;
  const pMax = hi + padv;
  const yOf = (p: number) => YBOT - (YBOT - YTOP) * ((p - pMin) / (pMax - pMin));

  const slot = (X1 - X0) / n;
  const bw = Math.min(slot * 0.6, 64);

  const up = (c: { o: number; c: number }) => c.c >= c.o;
  const colorOf = (c: { o: number; c: number }) =>
    up(c) ? theme.green : theme.red;

  const last = candles[n - 1];
  const first = candles[0];
  const pct = ((last.c - first.o) / first.o) * 100;
  const lastColor = colorOf(last);

  const fmt = (v: number) =>
    prefix + Math.round(v).toLocaleString("en-US") + suffix;

  const capWords = caption.split(" ");

  const revealStep = 4; // frames entre velas
  const lastPop = spring({
    frame: frame - (14 + n * revealStep),
    fps,
    config: { damping: 14, mass: 0.8 },
  });

  return (
    <StudioScene grid spotlightColor={pct >= 0 ? theme.green : theme.red}>
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
          {/* guia de cierre final */}
          {lastPop > 0.02 && (
            <line
              x1={X0}
              y1={yOf(last.c)}
              x2={X1}
              y2={yOf(last.c)}
              stroke={lastColor}
              strokeOpacity={0.45}
              strokeWidth={2}
              strokeDasharray="6 9"
            />
          )}
          {/* baseline */}
          <line x1={X0 - 10} y1={YBOT} x2={X1 + 10} y2={YBOT} stroke="#FFFFFF" strokeOpacity={0.1} strokeWidth={2} />

          {candles.map((c, i) => {
            const cx = X0 + slot * (i + 0.5);
            const color = colorOf(c);
            const isLast = i === n - 1;
            const pop = spring({
              frame: frame - (14 + i * revealStep),
              fps,
              config: { damping: 13, mass: 0.7 },
            });
            const a = Math.min(pop, 1);
            if (a <= 0.001) return null;
            const yH = yOf(c.h);
            const yL = yOf(c.l);
            const yO = yOf(c.o);
            const yC = yOf(c.c);
            const wickMid = (yH + yL) / 2;
            const bodyTop = Math.min(yO, yC);
            const bodyH = Math.max(Math.abs(yC - yO), 4);
            const glow = isLast && highlightLast;
            return (
              <g
                key={i}
                opacity={a}
                style={glow ? { filter: `drop-shadow(0 0 16px ${color})` } : undefined}
              >
                {/* mecha: crece desde el centro hacia high y low */}
                <line
                  x1={cx}
                  y1={wickMid - (wickMid - yH) * a}
                  x2={cx}
                  y2={wickMid + (yL - wickMid) * a}
                  stroke={color}
                  strokeWidth={4}
                  strokeLinecap="round"
                />
                {/* cuerpo: crece desde su centro vertical */}
                <rect
                  x={cx - bw / 2}
                  y={bodyTop + (bodyH * (1 - a)) / 2}
                  width={bw}
                  height={bodyH * a}
                  rx={5}
                  fill={color}
                  opacity={up(c) ? 0.96 : 0.92}
                />
              </g>
            );
          })}
        </svg>

        {/* lectura final: precio de cierre + % total */}
        <div
          style={{
            position: "absolute",
            top: YBOT + 24,
            width: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 28,
            opacity: Math.min(lastPop, 1),
            transform: `translateY(${(1 - Math.min(lastPop, 1)) * 18}px)`,
          }}
        >
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 30, fontWeight: 600, color: theme.textDim, letterSpacing: "0.04em", textTransform: "uppercase" }}>
              {readoutLabel}
            </div>
            <div
              style={{
                fontSize: 72,
                fontWeight: 900,
                color: lastColor,
                letterSpacing: "-0.02em",
                fontVariantNumeric: "tabular-nums",
                lineHeight: 1,
                textShadow: `0 0 34px ${lastColor}55`,
              }}
            >
              {fmt(last.c)}
            </div>
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "14px 24px",
              borderRadius: 18,
              background: `${lastColor}22`,
              border: `2px solid ${lastColor}66`,
              fontSize: 46,
              fontWeight: 900,
              color: lastColor,
              fontVariantNumeric: "tabular-nums",
            }}
          >
            {pct >= 0 ? "▲" : "▼"} {pct >= 0 ? "+" : "−"}
            {Math.abs(pct).toFixed(pct < 10 && pct > -10 ? 1 : 0)}%
          </div>
        </div>
      </AbsoluteFill>
    </StudioScene>
  );
};
