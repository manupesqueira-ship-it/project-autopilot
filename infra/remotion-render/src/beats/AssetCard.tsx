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
import { BrandLogo } from "../studio/BrandLogo";

export type AssetCardProps = {
  caption: string;
  name: string;
  ticker: string;
  logo?: string;
  spark: number[];
  priceLabel: string;
  priceValue: number;
  pricePrefix?: string;
  priceDecimals?: number;
  subline?: string;
  countEndFrame?: number;
};

// palette-ok-start: logo oficial de Google (marca) — colores reales obligatorios
const GoogleG: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 48 48">
    <path
      fill="#EA4335"
      d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"
    />
    <path
      fill="#4285F4"
      d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"
    />
    <path
      fill="#FBBC05"
      d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"
    />
    <path
      fill="#34A853"
      d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"
    />
  </svg>
);
// palette-ok-end

const fmt = (v: number, decimals: number) =>
  v.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

const CX = 110;
const CY = 430;
const CW = 860;
const CH = 1010;
const SX0 = CX + 90;
const SX1 = CX + CW - 90;
const SYTOP = CY + 470;
const SYBOT = CY + 690;

export const AssetCard: React.FC<AssetCardProps> = ({
  caption,
  name,
  ticker,
  logo = "google",
  spark,
  priceLabel,
  priceValue,
  pricePrefix = "$",
  priceDecimals = 2,
  subline,
  countEndFrame = 70,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const enter = spring({ frame: frame - 4, fps, config: { damping: 14, mass: 0.8 } });
  const breathe = Math.sin(frame / 14) * 4;

  // sparkline
  const n = spark.length;
  const vMax = Math.max(...spark);
  const vMin = Math.min(...spark);
  const xy = spark.map((v, i) => ({
    x: SX0 + ((SX1 - SX0) * i) / (n - 1),
    y: SYBOT - ((SYBOT - SYTOP) * (v - vMin)) / (vMax - vMin || 1),
  }));
  let total = 0;
  const cum = [0];
  for (let i = 0; i < n - 1; i++) {
    total += Math.hypot(xy[i + 1].x - xy[i].x, xy[i + 1].y - xy[i].y);
    cum.push(total);
  }
  const drawn = interpolate(frame, [16, countEndFrame], [0, total], {
    ...clamp,
    easing: Easing.bezier(0.3, 0.1, 0.3, 1),
  });
  const posAt = (len: number) => {
    const L = Math.min(Math.max(len, 0), total - 0.001);
    let i = 0;
    while (i < n - 2 && cum[i + 1] <= L) i++;
    const t = (L - cum[i]) / (cum[i + 1] - cum[i]);
    return {
      x: xy[i].x + (xy[i + 1].x - xy[i].x) * t,
      y: xy[i].y + (xy[i + 1].y - xy[i].y) * t,
    };
  };
  const dot = posAt(drawn);
  const linePath = xy.map((p, i) => `${i === 0 ? "M" : "L"}${p.x},${p.y}`).join(" ");
  const areaPath = `${linePath} L${xy[n - 1].x},${SYBOT + 26} L${xy[0].x},${SYBOT + 26} Z`;

  const shownPrice = interpolate(frame, [16, countEndFrame], [0, priceValue], {
    ...clamp,
    easing: Easing.bezier(0.2, 0.6, 0.35, 1),
  });
  const done = frame >= countEndFrame;
  const glowPulse = done ? 0.8 + Math.sin(frame / 9) * 0.2 : 1;

  const capWords = caption.split(" ");

  return (
    <StudioScene>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
        <div
          style={{
            position: "absolute",
            top: 300,
            width: "100%",
            textAlign: "center",
            fontSize: 42,
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
            left: CX,
            top: CY,
            width: CW,
            height: CH,
            borderRadius: 44,
            background:
              "linear-gradient(165deg, rgba(255,255,255,0.075) 0%, rgba(255,255,255,0.035) 55%, rgba(255,255,255,0.05) 100%)",
            border: "1.5px solid rgba(255,255,255,0.14)",
            boxShadow: `0 30px 80px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.12), 0 0 ${60 * glowPulse}px ${theme.green}14`,
            opacity: Math.min(enter * 1.3, 1),
            transform: `translateY(${(1 - enter) * 60 + breathe}px) scale(${0.94 + enter * 0.06})`,
          }}
        >
          <div
            style={{
              position: "absolute",
              top: 70,
              width: "100%",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 26,
            }}
          >
            <div
              style={{
                width: 168,
                height: 168,
                borderRadius: "50%",
                background: "#FFFFFF",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: `0 0 ${40 * glowPulse}px rgba(255,255,255,0.30), 0 14px 40px rgba(0,0,0,0.4)`,
              }}
            >
              {logo === "google" ? (
                <GoogleG size={96} />
              ) : (
                <BrandLogo slug={logo} size={96} on="light" />
              )}
            </div>
            <div style={{ fontSize: 60, fontWeight: 800, color: theme.text }}>
              {name}
            </div>
            <div
              style={{
                fontFamily: theme.mono,
                fontSize: 31,
                fontWeight: 500,
                color: theme.textDim,
                letterSpacing: "0.12em",
                marginTop: -14,
              }}
            >
              {ticker}
            </div>
          </div>
        </div>

        <svg
          width="1080"
          height="1920"
          style={{
            position: "absolute",
            opacity: Math.min(enter * 1.3, 1),
            transform: `translateY(${breathe}px)`,
          }}
        >
          <defs>
            <linearGradient id="sparkfill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={theme.green} stopOpacity="0.20" />
              <stop offset="100%" stopColor={theme.green} stopOpacity="0" />
            </linearGradient>
            <clipPath id="sparkclip">
              <rect x={SX0 - 4} y={0} width={Math.max(dot.x - SX0 + 6, 0)} height={1920} />
            </clipPath>
          </defs>
          <path d={areaPath} fill="url(#sparkfill)" clipPath="url(#sparkclip)" />
          <path
            d={linePath}
            fill="none"
            stroke={theme.green}
            strokeWidth={4.5}
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray={total}
            strokeDashoffset={total - drawn}
            style={{
              filter: `drop-shadow(0 0 9px ${theme.green}) drop-shadow(0 0 26px ${theme.green}55)`,
            }}
          />
          {drawn > 3 && (
            <g>
              <circle cx={dot.x} cy={dot.y} r={30} fill={theme.green} opacity={0.25} style={{ filter: "blur(12px)" }} />
              <circle
                cx={dot.x}
                cy={dot.y}
                r={15}
                fill={theme.green}
                style={{ filter: `drop-shadow(0 0 12px ${theme.green})` }}
              />
              <circle cx={dot.x - 4} cy={dot.y - 5} r={4.5} fill="white" opacity={0.85} />
            </g>
          )}
        </svg>

        <div
          style={{
            position: "absolute",
            left: CX,
            top: SYBOT + 70,
            width: CW,
            textAlign: "center",
            transform: `translateY(${breathe}px)`,
            opacity: Math.min(enter * 1.3, 1),
          }}
        >
          <div style={{ fontSize: 31, fontWeight: 500, color: theme.textDim }}>
            {priceLabel}
          </div>
          <div
            style={{
              fontSize: 104,
              fontWeight: 900,
              color: theme.gold,
              letterSpacing: "-0.02em",
              fontVariantNumeric: "tabular-nums",
              marginTop: 6,
              textShadow: done
                ? `0 0 ${40 * glowPulse}px ${theme.gold}88, 0 0 ${100 * glowPulse}px ${theme.gold}33`
                : `0 0 24px ${theme.gold}55`,
            }}
          >
            {pricePrefix}
            {fmt(shownPrice, priceDecimals)}
          </div>
        </div>

        {subline && (
          <div
            style={{
              position: "absolute",
              top: CY + CH + 60,
              width: "100%",
              textAlign: "center",
              fontSize: 42,
              fontWeight: 700,
              color: theme.text,
              opacity: interpolate(frame, [countEndFrame + 4, countEndFrame + 14], [0, 1], clamp),
              transform: `translateY(${(1 - spring({ frame: frame - countEndFrame - 4, fps, config: { damping: 13, mass: 0.6 } })) * 14}px)`,
            }}
          >
            {subline}
          </div>
        )}
      </AbsoluteFill>
    </StudioScene>
  );
};
