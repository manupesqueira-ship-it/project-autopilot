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

// Treemap: rectangulos con area proporcional al valor, embaldosados. Para
// "composicion de un portafolio / mercado por tamano". El item mas grande se
// resalta. Layout slice-and-dice alternando eje (deterministico, sin libreria).
export type TreemapProps = {
  caption: string;
  items: { label: string; value: number; color?: string }[];
  prefix?: string;
  suffix?: string;
  valueScale?: number;
  valueUnit?: string;
  asPercent?: boolean;
};

const X0 = 90;
const Y0 = 560;
const W = 900;
const H = 880;
// paleta CATEGORICA on-palette (Filtro A): verde/oro/teal/gris/teal/ambar. SIN rojo
// (rojo = SOLO perdida, regla semantica locked) ni azul/morado (reprueban Filtro A).
const PALETTE = [theme.green, theme.gold, "#5BC0BE", theme.textDim, "#1FA88B", "#E0A93C"];

type Rect = { x: number; y: number; w: number; h: number };

function tile(
  vals: number[],
  idx: number[],
  rect: Rect,
  horizontal: boolean
): { i: number; rect: Rect }[] {
  if (idx.length === 1) return [{ i: idx[0], rect }];
  const total = idx.reduce((a, k) => a + vals[k], 0) || 1;
  const frac = vals[idx[0]] / total;
  if (horizontal) {
    const w = rect.w * frac;
    return [
      { i: idx[0], rect: { ...rect, w } },
      ...tile(vals, idx.slice(1), { x: rect.x + w, y: rect.y, w: rect.w - w, h: rect.h }, !horizontal),
    ];
  }
  const h = rect.h * frac;
  return [
    { i: idx[0], rect: { ...rect, h } },
    ...tile(vals, idx.slice(1), { x: rect.x, y: rect.y + h, w: rect.w, h: rect.h - h }, !horizontal),
  ];
}

export const Treemap: React.FC<TreemapProps> = ({
  caption,
  items,
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

  const vals = items.map((it) => it.value);
  const total = vals.reduce((a, v) => a + v, 0) || 1;
  const order = items.map((_, i) => i).sort((a, b) => vals[b] - vals[a]);
  const placed = tile(vals, order, { x: X0, y: Y0, w: W, h: H }, W >= H);

  const fmt = (v: number) => {
    if (asPercent) return Math.round((v / total) * 100) + "%";
    const x = v / valueScale;
    return prefix + x.toLocaleString("en-US", { maximumFractionDigits: x < 10 ? 1 : 0 }) + valueUnit + suffix;
  };

  const pulse = 0.5 + 0.5 * Math.sin(frame / 11);
  const capWords = caption.split(" ");
  const GAP = 8;

  return (
    <StudioScene grid={false} spotlightColor={items[order[0]]?.color ?? theme.green}>
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

        {placed.map((p, k) => {
          const it = items[p.i];
          const color = it.color ?? PALETTE[p.i % PALETTE.length];
          const isBig = p.i === order[0];
          const appear = spring({ frame: frame - (12 + k * 8), fps, config: { damping: 15, mass: 0.8 } });
          const a = Math.min(appear, 1);
          const rw = p.rect.w - GAP;
          const rh = p.rect.h - GAP;
          const big = Math.min(rw, rh);
          return (
            <div
              key={p.i}
              style={{
                position: "absolute",
                left: p.rect.x + GAP / 2,
                top: p.rect.y + GAP / 2,
                width: rw,
                height: rh,
                borderRadius: 16,
                background: `linear-gradient(145deg, ${color}da, ${color}90)`,
                boxShadow: isBig ? `0 0 ${14 + pulse * 14}px ${color}88` : `0 4px 18px rgba(0,0,0,0.25)`,
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                padding: 14,
                boxSizing: "border-box",
                opacity: a,
                transform: `scale(${0.85 + a * 0.15})`,
                overflow: "hidden",
              }}
            >
              <div style={{ fontSize: Math.min(big * 0.22, 64), fontWeight: 900, color: "#0D1117", lineHeight: 1, fontVariantNumeric: "tabular-nums" }}>
                {fmt(it.value)}
              </div>
              <div style={{ fontSize: Math.min(big * 0.12, 30), fontWeight: 700, color: "#0D1117cc", marginTop: 6, textAlign: "center" }}>
                {it.label}
              </div>
            </div>
          );
        })}
      </AbsoluteFill>
    </StudioScene>
  );
};
