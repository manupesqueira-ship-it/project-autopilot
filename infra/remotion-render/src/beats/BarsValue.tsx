import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import { IglooStage } from "../studio/IglooStage";

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
// profundidad del slab 2.5D (cara superior iluminada + lateral en sombra).
// Sutil/premium (luz desde arriba-izq), NO 3D de juguete. Cierra el gap del
// teardown 0x100x: "barras con CUERPO, no rectangulos planos" (juez B).
const OX = 17;
const OY = 12;

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

  return (
    <IglooStage accent={theme.green} glowY={0.64}>
      <AbsoluteFill style={{ fontFamily: theme.font }}>
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
              <stop offset="60%" stopColor={theme.green} stopOpacity="0.55" />
              <stop offset="100%" stopColor={theme.green} stopOpacity="0.18" />
            </linearGradient>
            <linearGradient id="barD" x1="0" y1="1" x2="0" y2="0">
              <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.16" />
              <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0.04" />
            </linearGradient>
            {/* cara lateral en sombra: verde profundo, da el "cuerpo" del slab */}
            <linearGradient id="barGside" x1="0" y1="1" x2="0" y2="0">
              <stop offset="0%" stopColor="#067256" stopOpacity="0.95" />
              <stop offset="60%" stopColor="#067256" stopOpacity="0.5" />
              <stop offset="100%" stopColor="#067256" stopOpacity="0.16" />
            </linearGradient>
            {/* cara superior iluminada: capta la luz de arriba-izq */}
            <linearGradient id="barGtop" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#5FF0CE" stopOpacity="0.95" />
              <stop offset="100%" stopColor="#15C79C" stopOpacity="0.9" />
            </linearGradient>
            <linearGradient id="barDside" x1="0" y1="1" x2="0" y2="0">
              <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.08" />
              <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0.02" />
            </linearGradient>
            <linearGradient id="refl" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={theme.green} stopOpacity="0.14" />
              <stop offset="100%" stopColor={theme.green} stopOpacity="0" />
            </linearGradient>
            <filter id="cshadow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="10" />
            </filter>
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
            // todas las barras son esmeralda (un solo mundo); la heroe (Valor
            // actual) entra encendida + glow, la base queda en brasa tenue.
            const hero = b.highlight;
            const lit = hero && frame >= growAt(i);
            const x = cx - barW / 2;
            const top = BASE_Y - h;
            const w = barW;
            const topPts = `${x},${top} ${x + w},${top} ${x + w + OX},${top - OY} ${x + OX},${top - OY}`;
            const sidePts = `${x + w},${top} ${x + w + OX},${top - OY} ${x + w + OX},${BASE_Y - OY} ${x + w},${BASE_Y}`;
            return (
              <g key={i} opacity={hero ? 1 : 0.46}>
                <ellipse
                  cx={cx + OX * 0.4}
                  cy={BASE_Y + 10}
                  rx={w * 0.62}
                  ry={13}
                  fill="rgba(0,0,0,0.45)"
                  filter="url(#cshadow)"
                />
                <polygon points={sidePts} fill="url(#barGside)" />
                <polygon points={topPts} fill="url(#barGtop)" />
                <rect
                  x={x}
                  y={top}
                  width={w}
                  height={h}
                  rx={5}
                  fill="url(#barG)"
                  style={
                    lit
                      ? { filter: `drop-shadow(0 0 26px ${theme.green}66)` }
                      : undefined
                  }
                />
                <rect
                  x={x}
                  y={top}
                  width={w}
                  height={3}
                  rx={2}
                  fill={lit ? "rgba(220,255,245,0.9)" : "rgba(180,235,220,0.55)"}
                />
                {lit && (
                  <rect
                    x={x}
                    y={BASE_Y + 4}
                    width={w}
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
                  left: cx - 200,
                  top: BASE_Y - h - 86,
                  width: 400,
                  textAlign: "center",
                  fontSize: hl ? 56 : 42,
                  fontWeight: hl ? 500 : 300,
                  letterSpacing: "-0.01em",
                  color: hl ? theme.green : "#9FB2C2",
                  opacity: (hl ? 1 : 0.85) * Math.min(labelIn * 1.3, 1),
                  transform: `translateY(${(1 - labelIn) * 12}px)`,
                  textShadow: hl ? `0 0 34px ${theme.green}55` : undefined,
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
                  left: cx - 200,
                  top: BASE_Y + 30,
                  width: 400,
                  textAlign: "center",
                  fontSize: 26,
                  fontWeight: 300,
                  letterSpacing: "0.3em",
                  textTransform: "uppercase",
                  color: hl && frame >= growAt(i) ? "#C9D6E2" : "#7E8C9A",
                  opacity: Math.min(catIn * 1.3, 1),
                }}
              >
                {b.label}
              </div>
            </React.Fragment>
          );
        })}
      </AbsoluteFill>
    </IglooStage>
  );
};
