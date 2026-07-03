import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

// WaffleReveal — SI el contenido es "% de gente / proporción" (ej: 20 de 100 ahorra).
// Rulebook: waffle 10x10 gris; el subconjunto vira a verde UNO POR UNO (stagger ~1 frame)
// + micro-pop 1->1.08->1 + punch-in del cluster. Pop-out preatentivo (Von Restorff).

const GREEN = "#10b981", GRAY = "#3A3A3A", INK = "#F3EFE7", MUTE = "#9AA0AA";
const FONT = "InterVar, Inter, sans-serif";

export type WaffleRevealProps = {
  highlight?: number;      // cuántos de 100
  headline?: string;
  sub?: string;
  cue?: number;            // frame en que empieza el pop
};

export const WaffleReveal: React.FC<WaffleRevealProps> = ({
  highlight = 20,
  headline = "SOLO 20 DE 100",
  sub = "ahorra para su retiro",
  cue = 24,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const COLS = 10, ROWS = 10, R = 30, GAP = 34;
  const cell = R * 2 + GAP;                 // 94
  const gridW = COLS * cell - GAP;          // 906
  const x0 = 540 - gridW / 2 + R;           // centro
  const y0 = 690;

  // set resaltado = los últimos `highlight` (llena de abajo-derecha hacia arriba) => bloque legible
  const isHi = (i: number) => i >= 100 - highlight;
  // orden de activación dentro del set (para el stagger uno-por-uno)
  const hiOrder = new Map<number, number>();
  let k = 0;
  for (let i = 100 - highlight; i < 100; i++) hiOrder.set(i, k++);

  // punch-in del cluster cuando arranca el pop
  const punch = interpolate(frame, [cue, cue + 8, cue + highlight + 6], [1, 1.045, 1.02], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const gridO = interpolate(frame, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const hlO = interpolate(frame, [cue + highlight - 2, cue + highlight + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const dots = [];
  for (let i = 0; i < 100; i++) {
    const col = i % COLS, row = Math.floor(i / COLS);
    const cx = x0 + col * cell, cy = y0 + row * cell;
    let fill = GRAY, s = 1;
    if (isHi(i)) {
      const on = cue + (hiOrder.get(i) as number); // 1 frame por dot
      const t = frame - on;
      const appear = interpolate(frame, [on, on + 2], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
      fill = appear > 0 ? GREEN : GRAY;
      // micro-pop 1 -> 1.08 -> 1 en ~6 frames
      if (t >= 0 && t <= 7) s = interpolate(t, [0, 3, 7], [1, 1.16, 1], { extrapolateRight: "clamp" });
    }
    dots.push(<circle key={i} cx={cx} cy={cy} r={R} fill={fill} style={{ transform: `scale(${s})`, transformOrigin: `${cx}px ${cy}px`, transition: "none" }} />);
  }

  return (
    <AbsoluteFill style={{ backgroundColor: "#0A0B0D", fontFamily: FONT }}>
      <AbsoluteFill style={{ background: "radial-gradient(60% 40% at 50% 48%, rgba(16,185,129,0.10) 0%, transparent 60%)" }} />
      {/* masthead */}
      <div style={{ position: "absolute", top: 78, left: 96, fontSize: 27, fontWeight: 700, letterSpacing: "0.28em", color: INK }}>DINERO&nbsp;IA</div>
      <div style={{ position: "absolute", top: 130, left: 96, width: 888, height: 1, background: "#2B2F38" }} />

      <div style={{ position: "absolute", inset: 0, transform: `scale(${punch})`, transformOrigin: "50% 62%", opacity: gridO }}>
        <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>{dots}</svg>
      </div>

      {/* remate textual (aparece cuando termina el pop) */}
      <div style={{ position: "absolute", top: 300, left: 96, right: 96, textAlign: "center", fontSize: 96, fontWeight: 800, letterSpacing: "-0.01em", color: INK, opacity: hlO }}>{headline}</div>
      <div style={{ position: "absolute", top: 430, left: 96, right: 96, textAlign: "center", fontSize: 44, fontWeight: 500, color: MUTE, opacity: hlO }}>{sub}</div>
    </AbsoluteFill>
  );
};
