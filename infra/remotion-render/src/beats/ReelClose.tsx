import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

// ReelClose — cierre/CTA. Rulebook: cortar el ritmo, reconectar con el hook, loop.
const INK = "#F3EFE7", MUTE = "#9AA0AA", GREEN = "#10b981", ACCENT = "#E45B4E";
const FONT = "InterVar, Inter, sans-serif";

export type ReelCloseProps = { line1?: string; punch?: string; cta?: string };

export const ReelClose: React.FC<ReelCloseProps> = ({
  line1 = "Si el poder ya entró…",
  punch = "¿cuándo entras tú?",
  cta = "Guarda esto",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const l1 = interpolate(frame, [6, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const pk = spring({ frame: frame - 26, fps, config: { damping: 13, stiffness: 130 } });
  const ctaO = interpolate(frame, [50, 64], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const glow = interpolate(frame, [26, 44], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#08090B", fontFamily: FONT, justifyContent: "center", alignItems: "center" }}>
      <AbsoluteFill style={{ background: "radial-gradient(60% 40% at 50% 46%, rgba(16,185,129,0.10) 0%, transparent 60%)" }} />
      <div style={{ position: "absolute", top: 78, left: 96, fontSize: 27, fontWeight: 700, letterSpacing: "0.28em", color: INK }}>DINERO&nbsp;IA</div>
      <div style={{ fontSize: 58, fontWeight: 500, color: MUTE, opacity: l1, marginBottom: 24 }}>{line1}</div>
      <div style={{ fontSize: 118, fontWeight: 800, letterSpacing: "-0.02em", color: INK, transform: `scale(${0.9 + 0.1 * Math.min(1, pk)})`, filter: `drop-shadow(0 0 ${40 * glow}px rgba(16,185,129,0.5))`, textAlign: "center" }}>{punch}</div>
      <div style={{ position: "absolute", bottom: 300, display: "flex", alignItems: "center", gap: 18, opacity: ctaO }}>
        <div style={{ width: 20, height: 20, borderRadius: 5, background: GREEN }} />
        <div style={{ fontSize: 46, fontWeight: 700, color: INK }}>{cta}</div>
      </div>
    </AbsoluteFill>
  );
};
