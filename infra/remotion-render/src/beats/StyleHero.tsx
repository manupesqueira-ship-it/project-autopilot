import React from "react";
import { AbsoluteFill, Easing, interpolate, OffthreadVideo, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

// StyleHero — MISMO hook en 3 ESTILOS distintos, para elegir dirección hacia un look
// de REEL (con fondo/energía), no de presentación ejecutiva.
//   a = Editorial+ (papel elevado con glow)   b = Dark premium (igloo, luz volumétrica)
//   c = Fondo i2v (video tratado + número enorme)

const FONT = "InterVar, Inter, Georgia, serif";

export type StyleHeroProps = {
  variant?: "a" | "b" | "c";
  kicker?: string;
  big?: string;
  sub?: string;
  src?: string;      // i2v para variante c
};

export const StyleHero: React.FC<StyleHeroProps> = ({
  variant = "a",
  kicker = "EL COSTO REAL",
  big = "$1,074,962",
  sub = "Un café diario, en 20 años.",
  src = "i2v/bank_gold_liquid.mp4",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = Math.min(1, spring({ frame: frame - 10, fps, config: { damping: 12, stiffness: 130 } }));
  const kO = interpolate(frame, [2, 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const sO = interpolate(frame, [22, 38], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const breath = 0.9 + 0.1 * Math.sin(frame / 26);
  const drift = Math.sin(frame / 40) * 8;
  const grain = (op: number) => (
    <AbsoluteFill style={{ opacity: op, mixBlendMode: "overlay", pointerEvents: "none" }}>
      <svg width="1080" height="1920"><filter id="gn"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" /></filter><rect width="1080" height="1920" filter="url(#gn)" /></svg>
    </AbsoluteFill>
  );

  // ---------------- A · EDITORIAL+ (papel elevado) ----------------
  if (variant === "a") {
    return (
      <AbsoluteFill style={{ backgroundColor: "#F1ECE1", fontFamily: FONT }}>
        <div style={{ position: "absolute", left: 540 - 430 + drift, top: 900 - 430, width: 860, height: 860, borderRadius: "50%", background: "radial-gradient(circle, #9E2B2222 0%, #9E2B2209 42%, transparent 66%)", opacity: breath }} />
        <div style={{ position: "absolute", top: 78, left: 96, fontSize: 27, fontWeight: 700, letterSpacing: "0.28em", color: "#1B1712" }}>DINERO&nbsp;IA</div>
        <div style={{ position: "absolute", top: 130, left: 96, width: 888, height: 2, background: "#1B1712" }} />
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", textAlign: "center", padding: "0 70px" }}>
          <div style={{ fontSize: 34, fontWeight: 700, letterSpacing: "0.24em", color: "#9E2B22", opacity: kO }}>{kicker}</div>
          <div style={{ fontSize: 216, fontWeight: 800, letterSpacing: "-0.045em", lineHeight: 1, color: "#1B1712", margin: "26px 0", transform: `scale(${0.9 + 0.1 * pop})` }}>{big}</div>
          <div style={{ fontSize: 46, fontWeight: 500, color: "#5A544A", opacity: sO }}>{sub}</div>
        </AbsoluteFill>
        {grain(0.05)}
      </AbsoluteFill>
    );
  }

  // ---------------- B · DARK PREMIUM (igloo) ----------------
  if (variant === "b") {
    return (
      <AbsoluteFill style={{ backgroundColor: "#08090B", fontFamily: FONT }}>
        <div style={{ position: "absolute", left: 540 - 520 + drift, top: 420, width: 1040, height: 1040, borderRadius: "50%", background: "radial-gradient(circle, #35507E55 0%, #35507E1A 40%, transparent 68%)", opacity: breath }} />
        <div style={{ position: "absolute", left: 540 - 380 - drift, top: 1120, width: 760, height: 760, borderRadius: "50%", background: "radial-gradient(circle, #C9772E44 0%, transparent 62%)", opacity: 0.9 * breath }} />
        <div style={{ position: "absolute", top: 78, left: 96, fontSize: 27, fontWeight: 700, letterSpacing: "0.30em", color: "#C7CBD2" }}>DINERO&nbsp;IA</div>
        <div style={{ position: "absolute", top: 130, left: 96, width: 888, height: 1, background: "#2A2E36" }} />
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", textAlign: "center", padding: "0 70px" }}>
          <div style={{ fontSize: 34, fontWeight: 700, letterSpacing: "0.34em", color: "#D9A15C", opacity: kO }}>{kicker}</div>
          <div style={{ fontSize: 220, fontWeight: 800, letterSpacing: "-0.05em", lineHeight: 1, color: "#F4F1EA", margin: "26px 0", textShadow: "0 0 60px rgba(90,120,180,0.35)", transform: `scale(${0.9 + 0.1 * pop})` }}>{big}</div>
          <div style={{ fontSize: 46, fontWeight: 400, color: "#8B909B", opacity: sO }}>{sub}</div>
        </AbsoluteFill>
        {grain(0.08)}
      </AbsoluteFill>
    );
  }

  // ---------------- C · FONDO i2v (máxima energía) ----------------
  const zoom = 1.08 + interpolate(frame, [0, 130], [0, 0.08]);
  return (
    <AbsoluteFill style={{ backgroundColor: "#0A0A0B", fontFamily: FONT }}>
      <AbsoluteFill style={{ overflow: "hidden" }}>
        <OffthreadVideo src={staticFile(src)} muted loop style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${zoom})`, filter: "brightness(0.6) contrast(1.05) saturate(1.05)" }} />
      </AbsoluteFill>
      <AbsoluteFill style={{ background: "linear-gradient(to bottom, rgba(8,8,10,0.55) 0%, rgba(8,8,10,0.15) 42%, rgba(8,8,10,0.82) 100%)" }} />
      <div style={{ position: "absolute", top: 78, left: 96, fontSize: 27, fontWeight: 700, letterSpacing: "0.30em", color: "#F4F1EA" }}>DINERO&nbsp;IA</div>
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", textAlign: "center", padding: "0 60px" }}>
        <div style={{ fontSize: 36, fontWeight: 800, letterSpacing: "0.24em", color: "#F4C87A", opacity: kO }}>{kicker}</div>
        <div style={{ fontSize: 232, fontWeight: 800, letterSpacing: "-0.05em", lineHeight: 1, color: "#FFFFFF", margin: "24px 0", textShadow: "0 6px 40px rgba(0,0,0,0.5)", transform: `scale(${0.88 + 0.12 * pop})` }}>{big}</div>
        <div style={{ fontSize: 48, fontWeight: 500, color: "#ECE7DD", opacity: sO }}>{sub}</div>
      </AbsoluteFill>
      {grain(0.06)}
    </AbsoluteFill>
  );
};
