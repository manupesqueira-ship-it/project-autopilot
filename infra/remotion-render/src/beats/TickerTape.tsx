import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import { StudioScene } from "../studio/StudioScene";
import { BrandLogo } from "../studio/BrandLogo";

// Cinta de precios (stock ticker): chips con simbolo + precio + % que se
// desplazan en horizontal de forma continua (loop sin costura). Verde sube,
// rojo baja. Para "los mercados hoy". El scroll ES el micro-motion.
export type TickerTapeProps = {
  caption: string;
  items: { symbol: string; price: number; changePct: number; logo?: string }[];
  prefix?: string;
  decimals?: number;
  speed?: number; // px por frame
};

const ROWS = [
  { y: 760, dir: 1, speed: 3.2 },
  { y: 980, dir: -1, speed: 2.4 },
  { y: 1200, dir: 1, speed: 3.8 },
];

export const TickerTape: React.FC<TickerTapeProps> = ({
  caption,
  items,
  prefix = "$",
  decimals = 2,
  speed = 1,
}) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  const clamp = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
  };

  const fmt = (v: number) =>
    prefix + v.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });

  const chipW = 360;
  const tripleW = items.length * chipW;
  const capWords = caption.split(" ");

  const Chip: React.FC<{ it: TickerTapeProps["items"][number] }> = ({ it }) => {
    const up = it.changePct >= 0;
    const c = up ? theme.green : theme.red;
    return (
      <div
        style={{
          width: chipW - 24,
          margin: "0 12px",
          height: 150,
          borderRadius: 22,
          background: "rgba(255,255,255,0.04)",
          border: `1px solid ${c}44`,
          display: "flex",
          alignItems: "center",
          gap: 18,
          padding: "0 26px",
          boxSizing: "border-box",
        }}
      >
        {it.logo && <BrandLogo slug={it.logo} size={52} on="dark" />}
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ fontSize: 34, fontWeight: 800, color: theme.text }}>{it.symbol}</div>
          <div style={{ fontSize: 32, fontWeight: 700, color: theme.textDim, fontVariantNumeric: "tabular-nums" }}>{fmt(it.price)}</div>
        </div>
        <div style={{ marginLeft: "auto", fontSize: 32, fontWeight: 900, color: c, fontVariantNumeric: "tabular-nums" }}>
          {up ? "▲" : "▼"} {up ? "+" : "−"}{Math.abs(it.changePct).toFixed(1)}%
        </div>
      </div>
    );
  };

  return (
    <StudioScene grid spotlightColor={theme.green}>
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

        {ROWS.map((row, ri) => {
          // desplazamiento continuo con wrap modular (loop sin costura)
          const raw = (frame * row.speed * speed) % tripleW;
          const offset = row.dir > 0 ? -raw : raw - tripleW;
          // 3 copias para cubrir el ancho mientras hace loop
          return (
            <div
              key={ri}
              style={{
                position: "absolute",
                top: row.y,
                left: 0,
                width: tripleW * 3,
                display: "flex",
                transform: `translateX(${offset}px)`,
              }}
            >
              {[0, 1, 2].map((copy) =>
                items.map((it, i) => <Chip key={`${copy}-${i}`} it={it} />)
              )}
            </div>
          );
        })}

        {/* desvanecidos laterales para que la cinta entre/salga suave */}
        <AbsoluteFill
          style={{
            background: `linear-gradient(90deg, ${theme.bg.base} 0%, transparent 12%, transparent 88%, ${theme.bg.base} 100%)`,
            pointerEvents: "none",
          }}
        />
      </AbsoluteFill>
    </StudioScene>
  );
};
