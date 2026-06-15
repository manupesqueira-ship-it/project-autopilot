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

// Grafica "aguantó el desplome y se recuperó": tramo rojo (caida hasta el
// fondo) -> tramo verde (recuperacion que termina arriba = la ganancia).
// Inverso a LineChartSemantic. Reutilizable para narrativas de "buy the dip".
export type RecoveryChartProps = {
  caption: string;
  points: number[];
  troughIndex: number;
  labels?: { text: string; index: number; color?: string }[];
  troughLabel?: string;
  endLabel?: string;
};

const X0 = 90;
const X1 = 990;
const YTOP = 600;
const YBOT = 1300;

export const RecoveryChart: React.FC<RecoveryChartProps> = ({
  caption,
  points,
  troughIndex,
  labels = [],
  troughLabel,
  endLabel,
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

  // timeline: 6-66 cae rojo · 66-80 fondo+divisor · 80-148 recupera verde
  const redProg = interpolate(frame, [6, 66], [0, redLen], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.55, 0, 0.8, 1),
  });
  const greenProg = interpolate(frame, [80, 148], [redLen, total], {
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
  const dividerProg = interpolate(frame, [66, 80], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.2, 0, 0.3, 1),
  });

  const capWords = caption.split(" ");

  return (
    <StudioScene grid spotlightColor={onGreen ? theme.green : theme.red}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        <div
          style={{
            position: "absolute",
            top: 280,
            width: "100%",
            textAlign: "center",
            fontSize: 40,
            fontWeight: 500,
            color: theme.textDim,
            letterSpacing: "0.01em",
          }}
        >
          {capWords.map((w, i) => {
            const o = interpolate(frame, [2 + i * 3, 8 + i * 3], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            return (
              <span key={i} style={{ opacity: o }}>
                {w}{" "}
              </span>
            );
          })}
        </div>

        <svg width="1080" height="1920" style={{ position: "absolute" }}>
          <defs>
            <linearGradient id="rcRfill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={theme.red} stopOpacity="0.2" />
              <stop offset="55%" stopColor={theme.red} stopOpacity="0.06" />
              <stop offset="100%" stopColor={theme.red} stopOpacity="0" />
            </linearGradient>
            <linearGradient id="rcGfill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={theme.green} stopOpacity="0.18" />
              <stop offset="55%" stopColor={theme.green} stopOpacity="0.05" />
              <stop offset="100%" stopColor={theme.green} stopOpacity="0" />
            </linearGradient>
            <radialGradient id="rcDot" cx="32%" cy="28%" r="80%">
              <stop offset="0%" stopColor="#FFFFFF" />
              <stop offset="38%" stopColor={dotColor} />
              <stop offset="100%" stopColor={onGreen ? "#00684F" : "#7A1F1F"} />
            </radialGradient>
            <clipPath id="rcClipR">
              <rect x={X0 - 4} y={0} width={Math.max(dot.x - X0 + 6, 0)} height={1920} />
            </clipPath>
            <clipPath id="rcClipG">
              <rect x={trough.x} y={0} width={Math.max(dot.x - trough.x + 4, 0)} height={1920} />
            </clipPath>
          </defs>

          <path d={areaPath(0, troughIndex)} fill="url(#rcRfill)" clipPath="url(#rcClipR)" />
          {troughIndex < n - 1 && (
            <path d={areaPath(troughIndex, n - 1)} fill="url(#rcGfill)" clipPath="url(#rcClipG)" />
          )}

          {/* tramo rojo (caida) */}
          <path
            d={linePath(0, troughIndex)}
            fill="none"
            stroke={theme.red}
            strokeWidth={4.5}
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
          {/* tramo verde (recuperacion) */}
          {troughIndex < n - 1 && frame >= 80 && (
            <path
              d={linePath(troughIndex, n - 1)}
              fill="none"
              stroke={theme.green}
              strokeWidth={5}
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeDasharray={total - redLen}
              strokeDashoffset={total - redLen - Math.max(drawn - redLen, 0)}
              style={{ filter: `drop-shadow(0 0 10px ${theme.green}) drop-shadow(0 0 30px ${theme.green}55)` }}
            />
          )}
          {troughIndex < n - 1 && frame >= 80 && (
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
          )}

          {dividerProg > 0 && (
            <line
              x1={trough.x}
              y1={420}
              x2={trough.x}
              y2={420 + dividerProg * (YBOT + 40 - 420)}
              stroke="#FFFFFF"
              strokeWidth={3.5}
              opacity={1}
              style={{ filter: "drop-shadow(0 0 12px rgba(255,255,255,1)) drop-shadow(0 0 30px rgba(255,255,255,0.5))" }}
            />
          )}

          {drawn > 3 && drawn < total - 1 && (
            <g>
              <circle cx={dot.x} cy={dot.y} r={40} fill={dotColor} opacity={0.28} style={{ filter: "blur(14px)" }} />
              <circle
                cx={dot.x}
                cy={dot.y}
                r={23}
                fill="url(#rcDot)"
                style={{ filter: `drop-shadow(0 0 16px ${dotColor})` }}
              />
              <ellipse cx={dot.x - 7} cy={dot.y - 9} rx={7} ry={5} fill="white" opacity={0.85} />
            </g>
          )}
        </svg>

        {labels.map((lb, k) => {
          const p = xy[lb.index];
          const trigger = cum[lb.index];
          const appeared = drawn >= trigger - 1;
          const appearFrame =
            trigger <= redLen
              ? 6 + (trigger / Math.max(redLen, 1)) * 60
              : 80 + ((trigger - redLen) / Math.max(total - redLen, 1)) * 68;
          const s = appeared
            ? spring({ frame: frame - appearFrame, fps, config: { damping: 13, mass: 0.6 } })
            : 0;
          return (
            <div
              key={k}
              style={{
                position: "absolute",
                left: p.x - 200,
                top: p.y - 110,
                width: 400,
                textAlign: "center",
                fontSize: 42,
                fontWeight: 600,
                color: lb.color ?? theme.textDim,
                opacity: appeared ? Math.min(s * 1.4, 1) : 0,
                transform: `translateY(${(1 - s) * 16}px)`,
              }}
            >
              {lb.text}
            </div>
          );
        })}

        {troughLabel && (
          <div
            style={{
              position: "absolute",
              left: trough.x - 230,
              top: trough.y + 40,
              width: 460,
              textAlign: "center",
              fontSize: 50,
              fontWeight: 800,
              color: theme.red,
              opacity: interpolate(frame, [70, 80], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
              transform: `scale(${spring({ frame: frame - 70, fps, config: { damping: 11, mass: 0.7 } }) * 0.15 + 0.85})`,
              textShadow: `0 0 30px ${theme.red}66`,
            }}
          >
            {troughLabel}
          </div>
        )}

        {endLabel && (
          <div
            style={{
              position: "absolute",
              left: xy[n - 1].x - 380,
              top: xy[n - 1].y - 130,
              width: 400,
              textAlign: "right",
              fontSize: 58,
              fontWeight: 900,
              color: theme.green,
              opacity: interpolate(frame, [140, 150], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
              transform: `scale(${spring({ frame: frame - 140, fps, config: { damping: 11, mass: 0.7 } }) * 0.15 + 0.85})`,
              textShadow: `0 0 30px ${theme.green}66`,
            }}
          >
            {endLabel}
          </div>
        )}
      </AbsoluteFill>
    </StudioScene>
  );
};
