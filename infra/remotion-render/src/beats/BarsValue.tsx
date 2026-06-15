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

export type BarsProps = {
  caption: string;
  bars: { label: string; value: number; highlight?: boolean }[];
  prefix?: string;
  suffix?: string;
  // frame de arranque por barra (lo inyecta el ensamblador desde los
  // timestamps de la voz); fallback = stagger fijo
  growFrames?: number[];
  // chip protagonista que entra al inicio (p.ej. "$10,000") para que el
  // beat no tenga aire muerto antes del primer cue de voz
  intro?: string;
};

const STUB_H = 18;

const BASE_Y = 1280;
const MAX_H = 540;

export const BarsValue: React.FC<BarsProps> = ({
  caption,
  bars,
  prefix = "$",
  suffix = "",
  growFrames,
  intro,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const growAt = (i: number) => growFrames?.[i] ?? 10 + i * 7;
  const stubAt = (i: number) => 12 + i * 5;
  const barH = (i: number, v: number) => {
    const grow = spring({
      frame: frame - growAt(i),
      fps,
      config: { damping: 12, mass: 0.7 },
    });
    const stubIn = spring({
      frame: frame - stubAt(i),
      fps,
      config: { damping: 14, mass: 0.5 },
    });
    const breathe = 1 + Math.sin((frame - stubAt(i)) / 11 + i * 2.1) * 0.14;
    const grown = Math.max((v / vMax) * MAX_H, 24) * grow;
    return Math.max(STUB_H * stubIn * breathe, grown);
  };
  const introIn = spring({ frame: frame - 8, fps, config: { damping: 12, mass: 0.6 } });
  const introFloat = Math.sin(frame / 13) * 3;

  const n = bars.length;
  const vMax = Math.max(...bars.map((b) => b.value));
  const slot = 820 / n;
  const barW = Math.min(130, slot * 0.58);
  const x0 = (1080 - 820) / 2;

  const capWords = caption.split(" ");

  return (
    <StudioScene spotlightColor={theme.green}>
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

        {intro && (
          <div
            style={{
              position: "absolute",
              top: 420,
              width: "100%",
              textAlign: "center",
              transform: `translateY(${introFloat}px) scale(${0.9 + introIn * 0.1})`,
              opacity: Math.min(introIn * 1.4, 1),
            }}
          >
            <span
              style={{
                display: "inline-block",
                padding: "18px 44px",
                borderRadius: 60,
                border: `2px solid ${theme.gold}55`,
                background: `${theme.gold}14`,
                fontSize: 64,
                fontWeight: 800,
                color: theme.gold,
                textShadow: `0 0 26px ${theme.gold}55`,
                fontVariantNumeric: "tabular-nums",
              }}
            >
              {intro}
            </span>
          </div>
        )}

        <svg width="1080" height="1920" style={{ position: "absolute" }}>
          <defs>
            <linearGradient id="barG" x1="0" y1="1" x2="0" y2="0">
              <stop offset="0%" stopColor={theme.green} stopOpacity="0.95" />
              <stop offset="60%" stopColor={theme.green} stopOpacity="0.45" />
              <stop offset="100%" stopColor={theme.green} stopOpacity="0.12" />
            </linearGradient>
            <linearGradient id="barD" x1="0" y1="1" x2="0" y2="0">
              <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.16" />
              <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0.04" />
            </linearGradient>
            <linearGradient id="refl" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={theme.green} stopOpacity="0.14" />
              <stop offset="100%" stopColor={theme.green} stopOpacity="0" />
            </linearGradient>
          </defs>

          <line
            x1={x0 - 20}
            y1={BASE_Y}
            x2={x0 + 840}
            y2={BASE_Y}
            stroke="rgba(255,255,255,0.18)"
            strokeWidth={2}
          />

          {bars.map((b, i) => {
            const h = barH(i, b.value);
            const cx = x0 + slot * i + slot / 2;
            const hl = b.highlight && frame >= growAt(i);
            return (
              <g key={i}>
                <rect
                  x={cx - barW / 2}
                  y={BASE_Y - h}
                  width={barW}
                  height={h}
                  rx={10}
                  fill={hl ? "url(#barG)" : "url(#barD)"}
                  style={
                    hl
                      ? { filter: `drop-shadow(0 0 18px ${theme.green}66)` }
                      : undefined
                  }
                />
                {hl && (
                  <rect
                    x={cx - barW / 2}
                    y={BASE_Y + 4}
                    width={barW}
                    height={70}
                    rx={10}
                    fill="url(#refl)"
                  />
                )}
              </g>
            );
          })}
        </svg>

        {bars.map((b, i) => {
          const labelIn = spring({
            frame: frame - growAt(i) - 20,
            fps,
            config: { damping: 13, mass: 0.6 },
          });
          const catIn = spring({
            frame: frame - stubAt(i) - 6,
            fps,
            config: { damping: 13, mass: 0.6 },
          });
          const h = barH(i, b.value);
          const cx = x0 + (820 / n) * i + 820 / n / 2;
          const hl = b.highlight;
          return (
            <React.Fragment key={i}>
              <div
                style={{
                  position: "absolute",
                  left: cx - 160,
                  top: BASE_Y - h - 78,
                  width: 320,
                  textAlign: "center",
                  fontSize: hl ? 50 : 38,
                  fontWeight: hl ? 800 : 600,
                  color: hl ? theme.green : theme.textDim,
                  opacity: Math.min(labelIn * 1.3, 1),
                  transform: `translateY(${(1 - labelIn) * 12}px)`,
                  textShadow: hl ? `0 0 30px ${theme.green}66` : undefined,
                  fontVariantNumeric: "tabular-nums",
                }}
              >
                {prefix}
                {b.value.toLocaleString("en-US")}
                {suffix}
              </div>
              <div
                style={{
                  position: "absolute",
                  left: cx - 160,
                  top: BASE_Y + 26,
                  width: 320,
                  textAlign: "center",
                  fontSize: 30,
                  fontWeight: 500,
                  color: hl && frame >= growAt(i) ? theme.text : theme.textDim,
                  opacity: Math.min(catIn * 1.3, 1),
                }}
              >
                {b.label}
              </div>
            </React.Fragment>
          );
        })}
      </AbsoluteFill>
    </StudioScene>
  );
};
