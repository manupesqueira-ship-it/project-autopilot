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

export type LineChartProps = {
  caption: string;
  points: number[];
  peakIndex: number;
  labels: { text: string; index: number; color?: string }[];
  peakLabel?: string;
};

const X0 = 90;
const X1 = 990;
const YTOP = 600;
const YBOT = 1300;

// Mantener una caja de texto absoluta de `w`px dentro del frame 1080 (margen 16).
// Sin esto, un label sobre el último punto (x≈990, caja 400 centrada) se sale a
// 1190 y RECORTA el número — el bug exacto que arruinó R1.
const SAFE_X = 16;
const clampLabelLeft = (rawLeft: number, w: number) =>
  Math.min(Math.max(rawLeft, SAFE_X), 1080 - w - SAFE_X);

export const LineChartSemantic: React.FC<LineChartProps> = ({
  caption,
  points,
  peakIndex,
  labels,
  peakLabel,
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
  const greenLen = cum[peakIndex];

  // timeline: 6-78 dibuja verde · 78-88 pico+divisor · 88-148 cae rojo
  const greenProg = interpolate(frame, [6, 78], [0, greenLen], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.3, 0.1, 0.3, 1),
  });
  const redProg = interpolate(frame, [88, 148], [greenLen, total], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.55, 0, 0.8, 1),
  });
  const drawn = frame < 88 ? greenProg : redProg;

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
  const onRed = drawn > greenLen + 0.5;
  const dotColor = onRed ? theme.red : theme.green;

  const linePath = (from: number, to: number) =>
    xy
      .slice(from, to + 1)
      .map((p, i) => `${i === 0 ? "M" : "L"}${p.x},${p.y}`)
      .join(" ");
  const areaPath = (from: number, to: number) =>
    `${linePath(from, to)} L${xy[to].x},${YBOT + 40} L${xy[from].x},${YBOT + 40} Z`;

  const peak = xy[peakIndex];
  const dividerProg = interpolate(frame, [76, 88], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.2, 0, 0.3, 1),
  });

  const capWords = caption.split(" ");

  return (
    <StudioScene grid spotlightColor={onRed ? theme.red : theme.green}>
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
            <linearGradient id="gfill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={theme.green} stopOpacity="0.16" />
              <stop offset="55%" stopColor={theme.green} stopOpacity="0.05" />
              <stop offset="100%" stopColor={theme.green} stopOpacity="0" />
            </linearGradient>
            <linearGradient id="rfill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={theme.red} stopOpacity="0.2" />
              <stop offset="55%" stopColor={theme.red} stopOpacity="0.06" />
              <stop offset="100%" stopColor={theme.red} stopOpacity="0" />
            </linearGradient>
            <radialGradient id="dotg" cx="32%" cy="28%" r="80%">
              <stop offset="0%" stopColor="#FFFFFF" />
              <stop offset="38%" stopColor={dotColor} />
              <stop offset="100%" stopColor={onRed ? "#7A1F1F" : "#00684F"} />
            </radialGradient>
            <clipPath id="clipG">
              <rect x={X0 - 4} y={0} width={Math.max(dot.x - X0 + 6, 0)} height={1920} />
            </clipPath>
            <clipPath id="clipR">
              <rect x={peak.x} y={0} width={Math.max(dot.x - peak.x + 4, 0)} height={1920} />
            </clipPath>
          </defs>

          <path d={areaPath(0, peakIndex)} fill="url(#gfill)" clipPath="url(#clipG)" />
          {peakIndex < n - 1 && (
            <path d={areaPath(peakIndex, n - 1)} fill="url(#rfill)" clipPath="url(#clipR)" />
          )}

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
          <path
            d={linePath(0, peakIndex)}
            fill="none"
            stroke="#CFFFF2"
            strokeWidth={1.8}
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray={greenLen}
            strokeDashoffset={greenLen - Math.min(drawn, greenLen)}
            opacity={0.9}
          />
          {peakIndex < n - 1 && frame >= 88 && (
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
          {peakIndex < n - 1 && frame >= 88 && (
            <path
              d={linePath(peakIndex, n - 1)}
              fill="none"
              stroke="#FFDCDC"
              strokeWidth={1.6}
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeDasharray={total - greenLen}
              strokeDashoffset={total - greenLen - Math.max(drawn - greenLen, 0)}
              opacity={0.85}
            />
          )}

          {dividerProg > 0 && (
            <line
              x1={peak.x}
              y1={420}
              x2={peak.x}
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
                fill="url(#dotg)"
                style={{ filter: `drop-shadow(0 0 16px ${dotColor})` }}
              />
              <ellipse cx={dot.x - 7} cy={dot.y - 9} rx={7} ry={5} fill="white" opacity={0.85} />
            </g>
          )}
        </svg>

        {labels.map((lb, k) => {
          const p = xy[lb.index];
          const trigger = cum[lb.index];
          const appearFrame =
            trigger <= greenLen
              ? 6 + (trigger / Math.max(greenLen, 1)) * 72
              : 88 + ((trigger - greenLen) / Math.max(total - greenLen, 1)) * 60;
          const appeared = drawn >= trigger - 1;
          const s = appeared
            ? spring({ frame: frame - appearFrame, fps, config: { damping: 13, mass: 0.6 } })
            : 0;
          const LBL_W = 400;
          return (
            <div
              key={k}
              style={{
                position: "absolute",
                left: clampLabelLeft(p.x - LBL_W / 2, LBL_W),
                top: p.y - 110,
                width: LBL_W,
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

        {peakLabel && (
          <div
            style={{
              position: "absolute",
              left: clampLabelLeft(peak.x - 230, 460),
              top: peak.y - 150,
              width: 460,
              textAlign: "center",
              fontSize: 54,
              fontWeight: 800,
              color: theme.gold,
              opacity: interpolate(frame, [80, 88], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
              transform: `scale(${spring({ frame: frame - 80, fps, config: { damping: 11, mass: 0.7 } }) * 0.15 + 0.85})`,
              textShadow: `0 0 30px ${theme.gold}66`,
            }}
          >
            {peakLabel}
          </div>
        )}
      </AbsoluteFill>
    </StudioScene>
  );
};
