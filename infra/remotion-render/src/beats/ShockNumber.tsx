import React from "react";
import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

// ShockNumber — SI el contenido es "cifra shock" (perdió 40%, -$730 al año).
// Rulebook: número gris + count-up ease-out ~0.9s; punch-in 1->1.12 en <300ms en el
// aterrizaje; vira a color semántico (rojo pérdida / verde ganancia) + spring overshoot.
// Fondo negro mate, viñeta radial, CERO texto encima. Binding: el punch cae en el reveal.

const INK = "#F3EFE7", RED = "#ef4444", GREEN = "#10b981", MUTE = "#9AA0AA", ACCENT = "#E45B4E";
const FONT = "InterVar, Inter, sans-serif";

export type ShockNumberProps = {
  target?: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  valence?: "loss" | "gain";
  kicker?: string;
  caption?: string;
  land?: number;    // frame de aterrizaje del count-up
};

export const ShockNumber: React.FC<ShockNumberProps> = ({
  target = 730,
  prefix = "-$",
  suffix = "",
  decimals = 0,
  valence = "loss",
  kicker = "LO QUE PIERDES",
  caption = "cada año, sin invertir",
  land = 30,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const start = 6;
  const p = interpolate(frame, [start, land], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const val = target * p;
  const shown = prefix + val.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) + suffix;

  // punch-in en el aterrizaje: 1 -> 1.12 en ~8 frames, con spring overshoot al asentar
  const landed = frame >= land;
  const pop = spring({ frame: frame - land, fps, config: { damping: 9, stiffness: 200, mass: 0.7 } });
  const scale = landed ? 1 + 0.12 * (1 - Math.min(1, pop)) + 0.0 : interpolate(frame, [land - 6, land], [0.98, 1.0], { extrapolateLeft: "clamp" });
  // color: gris durante el conteo, vira al semantico en el aterrizaje
  const sem = valence === "loss" ? RED : GREEN;
  const colorMix = interpolate(frame, [land - 1, land + 4], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const color = colorMix > 0.5 ? sem : "#8A8F98";
  const kO = interpolate(frame, [10, 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const cO = interpolate(frame, [land + 4, land + 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const glow = colorMix > 0.5 ? `drop-shadow(0 0 60px ${sem}66)` : "none";

  return (
    <AbsoluteFill style={{ backgroundColor: "#08090B", fontFamily: FONT }}>
      <AbsoluteFill style={{ background: "radial-gradient(70% 50% at 50% 44%, rgba(255,255,255,0.05) 0%, transparent 55%)" }} />
      <AbsoluteFill style={{ background: "radial-gradient(120% 100% at 50% 44%, transparent 40%, rgba(0,0,0,0.7) 100%)" }} />
      {/* kicker arriba (no encima del numero) */}
      <div style={{ position: "absolute", top: 470, left: 0, right: 0, textAlign: "center", fontSize: 34, fontWeight: 700, letterSpacing: "0.24em", color: ACCENT, opacity: kO }}>{kicker}</div>
      {/* numero heroe */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ fontSize: 300, fontWeight: 800, letterSpacing: "-0.03em", color, transform: `scale(${scale})`, filter: glow, fontVariantNumeric: "tabular-nums" }}>{shown}</div>
      </AbsoluteFill>
      {/* caption abajo (aparece tras el aterrizaje) */}
      <div style={{ position: "absolute", bottom: 520, left: 96, right: 96, textAlign: "center", fontSize: 46, fontWeight: 500, color: MUTE, opacity: cO }}>{caption}</div>
    </AbsoluteFill>
  );
};
