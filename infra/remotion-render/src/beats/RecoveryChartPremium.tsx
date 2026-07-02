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
import { PremiumStage } from "../studio/PremiumStage";

// b4 — RECUPERACIÓN en el lenguaje premium aprobado (mismo mundo que
// HoldingsGainBars: PremiumStage + jerarquía limpia). La línea CAE en rojo
// (pérdida) desde el precio de adopción (~$44,739) hasta el fondo ($16,000) y se
// RECUPERA en verde hasta $64,000. Color semántico: rojo=SOLO la caída,
// verde=recuperación/ganancia. Sin título textual ENCIMA del chart: el contexto
// vive en el kicker (carril propio arriba). Datos EXACTOS del guion.

const W = 1080;
const X0 = 120;
const X1 = 960;
const YTOP = 690;
const YBOT = 1230;

export type RecoveryChartPremiumProps = {
  kicker?: string;
  points?: number[];
  troughIndex?: number;
  peakLabel?: string;
  troughLabel?: string;
  endLabel?: string;
};

export const RecoveryChartPremium: React.FC<RecoveryChartPremiumProps> = ({
  kicker = "Bitcoin · la caída que no los rindió",
  points = [44739, 40000, 35000, 28000, 22000, 16000, 18000, 23000, 30000, 38000, 45000, 55000, 64000],
  troughIndex = 5,
  peakLabel = "$44,739",
  troughLabel = "$16,000 USD",
  endLabel = "$64,000 USD",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const n = points.length;
  const vMax = Math.max(...points);
  const vMin = Math.min(...points);
  const pad = (vMax - vMin) * 0.1 || 1;
  const lo = vMin - pad;
  const hi = vMax + pad;

  const xy = points.map((v, i) => ({
    x: X0 + ((X1 - X0) * i) / (n - 1),
    y: YBOT - ((YBOT - YTOP) * (v - lo)) / (hi - lo),
  }));

  // longitudes de segmento (para dibujar la línea progresivamente)
  const segLen: number[] = [];
  let total = 0;
  for (let i = 0; i < n - 1; i++) {
    const L = Math.hypot(xy[i + 1].x - xy[i].x, xy[i + 1].y - xy[i].y);
    segLen.push(L);
    total += L;
  }
  const cum = [0];
  for (const L of segLen) cum.push(cum[cum.length - 1] + L);
  const redLen = cum[troughIndex];

  // timeline: 6-66 cae rojo · 66-80 fondo + divisor · 80-146 recupera verde
  const redProg = interpolate(frame, [6, 66], [0, redLen], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.55, 0, 0.8, 1),
  });
  const greenProg = interpolate(frame, [80, 146], [redLen, total], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.3, 0.1, 0.3, 1),
  });
  const drawn = frame < 80 ? redProg : greenProg;

  const posAt = (len: number) => {
    const L = Math.min(Math.max(len, 0), total - 0.001);
    let i = 0;
    while (i < n - 2 && cum[i + 1] <= L) i++;
    const t = (L - cum[i]) / segLen[i];
    return {
      x: xy[i].x + (xy[i + 1].x - xy[i].x) * t,
      y: xy[i].y + (xy[i + 1].y - xy[i].y) * t,
    };
  };
  const dot = posAt(drawn);
  const onGreen = drawn > redLen + 0.5;
  const dotColor = onGreen ? theme.green : theme.red;

  const linePath = (from: number, to: number) =>
    xy
      .slice(from, to + 1)
      .map((p, i) => `${i === 0 ? "M" : "L"}${p.x},${p.y}`)
      .join(" ");
  const areaPath = (from: number, to: number) =>
    `${linePath(from, to)} L${xy[to].x},${YBOT + 40} L${xy[from].x},${YBOT + 40} Z`;

  const trough = xy[troughIndex];
  const end = xy[n - 1];
  const peak = xy[0];

  const dividerProg = interpolate(frame, [66, 80], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.2, 0, 0.3, 1),
  });

  const peakAppear = interpolate(frame, [10, 24], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const troughAppear = interpolate(frame, [70, 82], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const troughPop = spring({ frame: frame - 70, fps, config: { damping: 11, mass: 0.7 } });
  const endAppear = interpolate(frame, [138, 150], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const endPop = spring({ frame: frame - 138, fps, config: { damping: 11, mass: 0.7 } });

  return (
    <PremiumStage tint={theme.green}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        {/* kicker de contexto (carril propio arriba, NO sobre el chart) */}
        <div
          style={{
            position: "absolute",
            top: 250,
            width: "100%",
            textAlign: "center",
            color: theme.textDim,
            fontSize: 30,
            fontWeight: 300,
            letterSpacing: "0.36em",
            textTransform: "uppercase",
            opacity: 0.85,
          }}
        >
          {kicker}
        </div>

        <svg width={W} height={1920} style={{ position: "absolute", inset: 0 }}>
          <defs>
            <linearGradient id="rcpRfill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={theme.red} stopOpacity="0.22" />
              <stop offset="55%" stopColor={theme.red} stopOpacity="0.06" />
              <stop offset="100%" stopColor={theme.red} stopOpacity="0" />
            </linearGradient>
            <linearGradient id="rcpGfill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={theme.green} stopOpacity="0.2" />
              <stop offset="55%" stopColor={theme.green} stopOpacity="0.05" />
              <stop offset="100%" stopColor={theme.green} stopOpacity="0" />
            </linearGradient>
            <radialGradient id="rcpDot" cx="32%" cy="28%" r="80%">
              <stop offset="0%" stopColor="#FFFFFF" />
              <stop offset="38%" stopColor={dotColor} />
              <stop offset="100%" stopColor={onGreen ? "#00684F" : "#7A1F1F"} />
            </radialGradient>
            <clipPath id="rcpClipR">
              <rect x={X0 - 6} y={0} width={Math.max(dot.x - X0 + 8, 0)} height={1920} />
            </clipPath>
            <clipPath id="rcpClipG">
              <rect x={trough.x} y={0} width={Math.max(dot.x - trough.x + 4, 0)} height={1920} />
            </clipPath>
          </defs>

          {/* línea base del chart (asienta sobre el piso del PremiumStage) */}
          <line
            x1={X0 - 6}
            y1={YBOT}
            x2={X1 + 6}
            y2={YBOT}
            stroke="rgba(255,255,255,0.18)"
            strokeWidth={2}
          />

          {/* áreas de relleno (rojo caída, verde recuperación) */}
          <path d={areaPath(0, troughIndex)} fill="url(#rcpRfill)" clipPath="url(#rcpClipR)" />
          {troughIndex < n - 1 && (
            <path d={areaPath(troughIndex, n - 1)} fill="url(#rcpGfill)" clipPath="url(#rcpClipG)" />
          )}

          {/* tramo ROJO (la caída) */}
          <path
            d={linePath(0, troughIndex)}
            fill="none"
            stroke={theme.red}
            strokeWidth={5}
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray={redLen}
            strokeDashoffset={redLen - Math.min(drawn, redLen)}
            style={{ filter: `drop-shadow(0 0 10px ${theme.red}) drop-shadow(0 0 30px ${theme.red}55)` }}
          />
          <path
            d={linePath(0, troughIndex)}
            fill="none"
            stroke="#FFDCDC"
            strokeWidth={1.6}
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray={redLen}
            strokeDashoffset={redLen - Math.min(drawn, redLen)}
            opacity={0.85}
          />

          {/* tramo VERDE (la recuperación) */}
          {troughIndex < n - 1 && frame >= 80 && (
            <>
              <path
                d={linePath(troughIndex, n - 1)}
                fill="none"
                stroke={theme.green}
                strokeWidth={5.5}
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeDasharray={total - redLen}
                strokeDashoffset={total - redLen - Math.max(drawn - redLen, 0)}
                style={{ filter: `drop-shadow(0 0 10px ${theme.green}) drop-shadow(0 0 30px ${theme.green}55)` }}
              />
              <path
                d={linePath(troughIndex, n - 1)}
                fill="none"
                stroke="#CFFFF2"
                strokeWidth={1.8}
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeDasharray={total - redLen}
                strokeDashoffset={total - redLen - Math.max(drawn - redLen, 0)}
                opacity={0.9}
              />
            </>
          )}

          {/* divisor blanco que marca el FONDO (el punto de inflexión) */}
          {dividerProg > 0 && (
            <line
              x1={trough.x}
              y1={460}
              x2={trough.x}
              y2={460 + dividerProg * (YBOT - 460)}
              stroke="#FFFFFF"
              strokeWidth={3}
              strokeDasharray="2 10"
              opacity={0.5}
            />
          )}

          {/* punto de adopción (origen, tenue) */}
          {peakAppear > 0.01 && (
            <circle cx={peak.x} cy={peak.y} r={6} fill={theme.textDim} opacity={peakAppear * 0.8} />
          )}

          {/* punto brillante viajero (la cabeza de la línea) */}
          {drawn > 3 && drawn < total - 1 && (
            <g>
              <circle cx={dot.x} cy={dot.y} r={40} fill={dotColor} opacity={0.28} style={{ filter: "blur(14px)" }} />
              <circle cx={dot.x} cy={dot.y} r={22} fill="url(#rcpDot)" style={{ filter: `drop-shadow(0 0 16px ${dotColor})` }} />
              <ellipse cx={dot.x - 7} cy={dot.y - 9} rx={7} ry={5} fill="white" opacity={0.85} />
            </g>
          )}

          {/* punto final fijo (el remate verde) */}
          {endAppear > 0.01 && (
            <g>
              <circle cx={end.x} cy={end.y} r={42} fill={theme.green} opacity={0.3 * endAppear} style={{ filter: "blur(14px)" }} />
              <circle cx={end.x} cy={end.y} r={14} fill={theme.green} opacity={endAppear} style={{ filter: `drop-shadow(0 0 16px ${theme.green})` }} />
            </g>
          )}
        </svg>

        {/* etiqueta PRECIO DE ADOPCIÓN (origen, tenue, ancla izquierda) */}
        <div
          style={{
            position: "absolute",
            left: 84,
            top: peak.y - 78,
            width: 320,
            textAlign: "left",
            opacity: peakAppear,
          }}
        >
          <div style={{ fontSize: 24, fontWeight: 500, letterSpacing: "0.12em", textTransform: "uppercase", color: theme.textDim, opacity: 0.8 }}>
            Compraron desde
          </div>
          <div style={{ marginTop: 4, fontSize: 38, fontWeight: 700, color: theme.textDim, fontVariantNumeric: "tabular-nums" }}>
            {peakLabel}
          </div>
        </div>

        {/* etiqueta FONDO (rojo, prominente, bajo el trough) */}
        <div
          style={{
            position: "absolute",
            left: trough.x - 240,
            top: YBOT + 28,
            width: 480,
            textAlign: "center",
            opacity: troughAppear,
            transform: `scale(${0.85 + troughPop * 0.15})`,
          }}
        >
          <div style={{ fontSize: 24, fontWeight: 600, letterSpacing: "0.18em", textTransform: "uppercase", color: theme.red, opacity: 0.82 }}>
            El fondo
          </div>
          <div style={{ marginTop: 4, fontSize: 70, fontWeight: 800, color: theme.red, fontVariantNumeric: "tabular-nums", letterSpacing: "-0.01em", textShadow: `0 0 30px ${theme.red}55` }}>
            {troughLabel}
          </div>
        </div>

        {/* etiqueta REMATE (verde, el clímax de la recuperación). Ancla derecha,
            ARRIBA-IZQUIERDA del punto verde para no encimarse; una sola línea. */}
        <div
          style={{
            position: "absolute",
            left: 400,
            top: end.y - 152,
            width: 510,
            textAlign: "right",
            opacity: endAppear,
            transform: `translateY(${(1 - endPop) * 16}px)`,
          }}
        >
          <div style={{ fontSize: 26, fontWeight: 600, letterSpacing: "0.16em", textTransform: "uppercase", color: theme.green, opacity: 0.9 }}>
            Se disparó a
          </div>
          <div style={{ marginTop: 4, fontSize: 72, fontWeight: 800, color: theme.green, fontVariantNumeric: "tabular-nums", letterSpacing: "-0.02em", whiteSpace: "nowrap", textShadow: `0 0 40px ${theme.green}66` }}>
            {endLabel}
          </div>
        </div>
      </AbsoluteFill>
    </PremiumStage>
  );
};
