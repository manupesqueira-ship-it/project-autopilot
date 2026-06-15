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

export type TrendBreakProps = {
  caption: string;
  points: number[];
  peakIndex: number;
  counterLabel: string;
  countFrom: number;
  countTo: number;
  countPrefix?: string;
  pctLabel?: string;
  peakLabel?: string;
  troughLabel?: string;
  // inyectados por el ensamblador desde los timestamps de la voz
  breakFrame?: number;
  countEndFrame?: number;
};

const X0 = 90;
const X1 = 990;
const YTOP = 820;
const YBOT = 1430;

const fmt = (v: number) =>
  Math.round(v).toLocaleString("en-US");

export const TrendBreak: React.FC<TrendBreakProps> = ({
  caption,
  points,
  peakIndex,
  counterLabel,
  countFrom,
  countTo,
  countPrefix = "$",
  pctLabel,
  peakLabel,
  troughLabel,
  breakFrame = 45,
  countEndFrame,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames: d } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };
  const fallEnd = countEndFrame ?? d - 30;

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
  const greenLen = cum[peakIndex];

  const fallStart = breakFrame + 6;
  const greenProg = interpolate(frame, [8, breakFrame], [0, greenLen], {
    ...clamp,
    easing: Easing.bezier(0.3, 0.1, 0.3, 1),
  });
  const redProg = interpolate(frame, [fallStart, fallEnd], [greenLen, total], {
    ...clamp,
    easing: Easing.bezier(0.5, 0.05, 0.7, 1),
  });
  const drawn = frame < fallStart ? greenProg : redProg;
  const onRed = drawn > greenLen + 0.5;

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
  const dotColor = onRed ? theme.red : theme.green;

  const linePath = (from: number, to: number) =>
    xy
      .slice(from, to + 1)
      .map((p, i) => `${i === 0 ? "M" : "L"}${p.x},${p.y}`)
      .join(" ");
  const areaPath = (from: number, to: number) =>
    `${linePath(from, to)} L${xy[to].x},${YBOT + 40} L${xy[from].x},${YBOT + 40} Z`;

  const peak = xy[peakIndex];
  const trough = xy[n - 1];
  const dividerProg = interpolate(frame, [breakFrame - 4, breakFrame + 6], [0, 1], {
    ...clamp,
    easing: Easing.bezier(0.2, 0, 0.3, 1),
  });

  // sacudida al quiebre
  const shakeT = frame - breakFrame;
  const shake =
    shakeT >= 0 && shakeT < 10
      ? Math.sin(shakeT * 1.9) * 7 * (1 - shakeT / 10)
      : 0;

  // counter cayendo con la voz
  const shown = interpolate(frame, [fallStart, fallEnd], [countFrom, countTo], {
    ...clamp,
    easing: Easing.bezier(0.5, 0.05, 0.7, 1),
  });
  const counterColor = onRed ? theme.red : theme.gold;
  const fallDone = frame >= fallEnd;
  const glowPulse = fallDone ? 0.8 + Math.sin(frame / 9) * 0.2 : 1;

  const troughIn = spring({
    frame: frame - fallEnd,
    fps,
    config: { damping: 12, mass: 0.7 },
  });

  const capWords = caption.split(" ");

  return (
    <StudioScene spotlightColor={onRed ? theme.red : theme.green}>
      <AbsoluteFill
        style={{ fontFamily: theme.font, transform: `translateX(${shake}px)` }}
      >
        <div
          style={{
            position: "absolute",
            top: 270,
            width: "100%",
            textAlign: "center",
            fontSize: 40,
            fontWeight: 500,
            color: theme.textDim,
          }}
        >
          {capWords.map((w, i) => {
            const o = interpolate(frame, [2 + i * 3, 8 + i * 3], [0, 1], clamp);
            return (
              <span key={i} style={{ opacity: o }}>
                {w}{" "}
              </span>
            );
          })}
        </div>

        <div
          style={{
            position: "absolute",
            top: 380,
            width: "100%",
            textAlign: "center",
            fontSize: 33,
            fontWeight: 500,
            color: theme.textDim,
            opacity: interpolate(frame, [10, 18], [0, 1], clamp),
          }}
        >
          {counterLabel}
        </div>
        <div
          style={{
            position: "absolute",
            top: 430,
            width: "100%",
            textAlign: "center",
            fontSize: 124,
            fontWeight: 900,
            color: counterColor,
            letterSpacing: "-0.02em",
            fontVariantNumeric: "tabular-nums",
            textShadow: `0 0 ${44 * glowPulse}px ${counterColor}88, 0 0 ${110 * glowPulse}px ${counterColor}33`,
            opacity: interpolate(frame, [10, 18], [0, 1], clamp),
            transform: `translateY(${Math.sin(frame / 13) * 3}px)`,
          }}
        >
          {countPrefix}
          {fmt(shown)}
        </div>

        <svg width="1080" height="1920" style={{ position: "absolute" }}>
          <defs>
            <linearGradient id="tb_g" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={theme.green} stopOpacity="0.16" />
              <stop offset="100%" stopColor={theme.green} stopOpacity="0" />
            </linearGradient>
            <linearGradient id="tb_r" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={theme.red} stopOpacity="0.24" />
              <stop offset="60%" stopColor={theme.red} stopOpacity="0.07" />
              <stop offset="100%" stopColor={theme.red} stopOpacity="0" />
            </linearGradient>
            <radialGradient id="tb_dot" cx="32%" cy="28%" r="80%">
              <stop offset="0%" stopColor="#FFFFFF" />
              <stop offset="38%" stopColor={dotColor} />
              <stop offset="100%" stopColor={onRed ? "#7A1F1F" : "#00684F"} />
            </radialGradient>
            <clipPath id="tb_cg">
              <rect x={X0 - 4} y={0} width={Math.max(dot.x - X0 + 6, 0)} height={1920} />
            </clipPath>
            <clipPath id="tb_cr">
              <rect x={peak.x} y={0} width={Math.max(dot.x - peak.x + 4, 0)} height={1920} />
            </clipPath>
          </defs>

          <path d={areaPath(0, peakIndex)} fill="url(#tb_g)" clipPath="url(#tb_cg)" />
          <path d={areaPath(peakIndex, n - 1)} fill="url(#tb_r)" clipPath="url(#tb_cr)" />

          <path
            d={linePath(0, peakIndex)}
            fill="none"
            stroke={theme.green}
            strokeWidth={5}
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray={greenLen}
            strokeDashoffset={greenLen - Math.min(drawn, greenLen)}
            style={{
              filter: `drop-shadow(0 0 10px ${theme.green}) drop-shadow(0 0 30px ${theme.green}55)`,
            }}
          />
          {frame >= fallStart && (
            <path
              d={linePath(peakIndex, n - 1)}
              fill="none"
              stroke={theme.red}
              strokeWidth={4.5}
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeDasharray={total - greenLen}
              strokeDashoffset={total - greenLen - Math.max(drawn - greenLen, 0)}
              style={{
                filter: `drop-shadow(0 0 10px ${theme.red}) drop-shadow(0 0 30px ${theme.red}55)`,
              }}
            />
          )}

          {dividerProg > 0 && (
            <line
              x1={peak.x}
              y1={640}
              x2={peak.x}
              y2={640 + dividerProg * (YBOT + 40 - 640)}
              stroke="#FFFFFF"
              strokeWidth={3.5}
              style={{
                filter:
                  "drop-shadow(0 0 12px rgba(255,255,255,1)) drop-shadow(0 0 30px rgba(255,255,255,0.5))",
              }}
            />
          )}

          {drawn > 3 && (
            <g>
              <circle cx={dot.x} cy={dot.y} r={40} fill={dotColor} opacity={0.28} style={{ filter: "blur(14px)" }} />
              <circle
                cx={dot.x}
                cy={dot.y}
                r={23}
                fill="url(#tb_dot)"
                style={{ filter: `drop-shadow(0 0 16px ${dotColor})` }}
              />
              <ellipse cx={dot.x - 7} cy={dot.y - 9} rx={7} ry={5} fill="white" opacity={0.85} />
            </g>
          )}
        </svg>

        {peakLabel && (
          <div
            style={{
              position: "absolute",
              left: peak.x - 200,
              top: peak.y - 130,
              width: 400,
              textAlign: "center",
              fontSize: 48,
              fontWeight: 800,
              color: theme.gold,
              opacity: interpolate(frame, [breakFrame - 4, breakFrame + 4], [0, 1], clamp),
              textShadow: `0 0 28px ${theme.gold}66`,
            }}
          >
            {peakLabel}
          </div>
        )}

        {troughLabel && (
          <div
            style={{
              position: "absolute",
              left: trough.x - 360,
              top: trough.y - 120,
              width: 400,
              textAlign: "right",
              fontSize: 48,
              fontWeight: 800,
              color: theme.red,
              opacity: fallDone ? Math.min(troughIn * 1.4, 1) : 0,
              transform: `translateY(${(1 - troughIn) * 16}px)`,
              textShadow: `0 0 28px ${theme.red}66`,
            }}
          >
            {troughLabel}
          </div>
        )}

        {pctLabel && (
          <div
            style={{
              position: "absolute",
              left: 540 - 130,
              top: 690,
              width: 260,
              textAlign: "center",
              fontSize: 52,
              fontWeight: 900,
              color: theme.red,
              padding: "10px 0",
              borderRadius: 22,
              background: "rgba(255,107,107,0.10)",
              border: `1.5px solid ${theme.red}55`,
              opacity: fallDone ? Math.min(troughIn * 1.4, 1) : 0,
              transform: `scale(${0.85 + troughIn * 0.15})`,
              textShadow: `0 0 30px ${theme.red}88`,
            }}
          >
            {pctLabel}
          </div>
        )}
      </AbsoluteFill>
    </StudioScene>
  );
};
