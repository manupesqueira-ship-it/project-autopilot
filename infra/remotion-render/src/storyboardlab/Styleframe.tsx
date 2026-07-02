import React from "react";
import { AbsoluteFill } from "remotion";
import { theme } from "../theme";
import { StyleframeSpec, Block, Align } from "./types";

export const LAB_W = 1080;
export const LAB_H = 1920;

// Safe-areas en px sobre 1080x1920 (incluye zonas de UI de IG que tapan contenido).
export const SAFE = { action: 96, title: 192 };
const UI_ZONES = [
  { name: "perfil / arriba", x: 0, y: 0, w: LAB_W, h: 210 },
  { name: "caption / abajo", x: 0, y: LAB_H - 340, w: LAB_W, h: 340 },
  { name: "acciones / der.", x: LAB_W - 150, y: LAB_H - 980, w: 150, h: 620 },
];

const F = theme.font;

function renderBlock(b: Block, i: number): React.ReactNode {
  const base: React.CSSProperties = { position: "absolute", left: b.x, top: b.y, fontFamily: F };
  if (b.type === "rect") {
    return <div key={i} style={{ ...base, width: b.w, height: b.h, background: b.fill ?? "rgba(255,255,255,0.04)", border: b.stroke ? `2px solid ${b.stroke}` : "none", borderRadius: b.radius ?? 16 }} />;
  }
  if (b.type === "divider") {
    return <div key={i} style={{ ...base, width: b.w, height: b.thickness ?? 2, background: b.color ?? "rgba(255,255,255,0.14)" }} />;
  }
  if (b.type === "chartph" || b.type === "objectph") {
    const circle = b.type === "objectph" && b.shape === "circle";
    const arrow = b.type === "chartph" ? (b.trend === "down" ? "↘" : b.trend === "up" ? "↗" : "→") : "◉";
    return (
      <div key={i} style={{ ...base, width: b.w, height: b.h, border: `2px dashed ${theme.textDim}`, borderRadius: circle ? b.w / 2 : 18, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", color: theme.textDim, gap: 10 }}>
        <div style={{ fontSize: 64, opacity: 0.5 }}>{arrow}</div>
        <div style={{ fontSize: 26, opacity: 0.8, textAlign: "center", padding: "0 16px" }}>{b.label ?? (b.type === "chartph" ? "[chart]" : "[objeto / i2v]")}</div>
      </div>
    );
  }
  // text / number / label
  const align: Align = (b as { align?: Align }).align ?? "left";
  const isNum = b.type === "number";
  return (
    <div
      key={i}
      style={{
        ...base,
        width: (b as { w?: number }).w ?? undefined,
        textAlign: align,
        fontSize: b.size ?? (b.type === "label" ? 36 : 48),
        color: (b as { color?: string }).color ?? (b.type === "label" ? theme.textDim : theme.text),
        fontWeight: isNum ? 800 : (b as { weight?: number }).weight ?? (b.type === "label" ? 600 : 700),
        letterSpacing: (b as { letterSpacing?: number }).letterSpacing ?? (b.type === "label" ? 2 : 0),
        fontVariantNumeric: isNum ? "tabular-nums" : undefined,
        opacity: (b as { opacity?: number }).opacity ?? 1,
        lineHeight: 1.1,
        textTransform: b.type === "label" ? "uppercase" : undefined,
      }}
    >
      {b.text}
    </div>
  );
}

const Overlay: React.FC<{ x: number; y: number; w: number; h: number; color: string; dashed?: boolean; label?: string }> = ({ x, y, w, h, color, dashed, label }) => (
  <div style={{ position: "absolute", left: x, top: y, width: w, height: h, border: `2px ${dashed ? "dashed" : "solid"} ${color}`, boxSizing: "border-box", pointerEvents: "none" }}>
    {label ? <div style={{ position: "absolute", top: 4, left: 8, fontSize: 22, color, fontFamily: F, opacity: 0.9 }}>{label}</div> : null}
  </div>
);

export const Styleframe: React.FC<{
  spec: StyleframeSpec;
  showSafe?: boolean;
  showGrid?: boolean;
  showUI?: boolean;
  gridCols?: number;
}> = ({ spec, showSafe = true, showGrid = false, showUI = true, gridCols = 12 }) => {
  const bg = spec.bg === "base" ? theme.bg.base : theme.bg.gradient;
  const cols = Math.max(1, gridCols);
  const inner = LAB_W - SAFE.title * 2;
  const colW = inner / cols;
  return (
    <AbsoluteFill style={{ background: bg }}>
      {/* grano sutil para no juzgar sobre un negro plano */}
      <AbsoluteFill style={{ background: "radial-gradient(120% 80% at 50% 28%, rgba(91,192,190,0.06), rgba(0,0,0,0) 60%)" }} />

      {spec.blocks.map((b, i) => renderBlock(b, i))}

      {showGrid &&
        Array.from({ length: cols + 1 }).map((_, i) => (
          <div key={`g${i}`} style={{ position: "absolute", top: 0, bottom: 0, left: SAFE.title + i * colW, width: 1, background: "rgba(0,217,165,0.10)" }} />
        ))}

      {showUI && UI_ZONES.map((z, i) => <Overlay key={`ui${i}`} {...z} color="rgba(255,107,107,0.45)" dashed label={z.name} />)}

      {showSafe && (
        <>
          <Overlay x={SAFE.action} y={SAFE.action} w={LAB_W - SAFE.action * 2} h={LAB_H - SAFE.action * 2} color="rgba(255,255,255,0.22)" label="action-safe 5%" />
          <Overlay x={SAFE.title} y={SAFE.title} w={LAB_W - SAFE.title * 2} h={LAB_H - SAFE.title * 2} color="rgba(212,165,116,0.45)" label="title-safe 10%" />
        </>
      )}

      {spec.title ? (
        <div style={{ position: "absolute", top: 18, left: 0, width: LAB_W, textAlign: "center", fontFamily: F, fontSize: 22, color: "rgba(255,255,255,0.5)" }}>
          {spec.id} · {spec.title}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
