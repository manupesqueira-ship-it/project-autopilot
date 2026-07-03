import React from "react";
import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

// TypeAB — arbitraje de look EN PÍXELES (auditoría 2026-07-03, salto paso 1).
// Mismo contenido, dos lenguajes:
//   variant "bold"  = lo que renderizamos hoy (Inter 800, bg #08090B)
//   variant "thin"  = la biblia igloo que dictó Manuel (negro mate #070707, grotesca
//                     FINÍSIMA, MAYÚS tracking ancho, restricción extrema, 1 acento)
const FONT = "InterVar, Inter, sans-serif";

export type TypeABProps = { variant?: "bold" | "thin" };

export const TypeAB: React.FC<TypeABProps> = ({ variant = "thin" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const land = 40;
  const p = interpolate(frame, [8, land], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const val = 32234 * p;
  const shown = "$" + Math.round(val).toLocaleString("en-US");
  const landed = frame >= land;
  const pop = spring({ frame: frame - land, fps, config: { damping: 200 } });
  const scale = landed ? 1 + 0.05 * (1 - pop) : 1;
  const colorMix = interpolate(frame, [land - 1, land + 4], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const kO = interpolate(frame, [12, 26], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const cO = interpolate(frame, [land + 6, land + 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  if (variant === "bold") {
    // === LO DE HOY: Inter 800, #08090B, esmeralda/rojo saturado ===
    const color = colorMix > 0.5 ? "#ef4444" : "#8A8F98";
    return (
      <AbsoluteFill style={{ backgroundColor: "#08090B", fontFamily: FONT }}>
        <AbsoluteFill style={{ background: "radial-gradient(70% 50% at 50% 44%, rgba(255,255,255,0.05) 0%, transparent 55%)" }} />
        <div style={{ position: "absolute", top: 78, left: 96, fontSize: 27, fontWeight: 700, letterSpacing: "0.28em", color: "#F3EFE7" }}>DINERO&nbsp;IA</div>
        <div style={{ position: "absolute", top: 470, left: 0, right: 0, textAlign: "center", fontSize: 34, fontWeight: 700, letterSpacing: "0.24em", color: "#E45B4E", opacity: kO }}>TERMINAS PAGANDO</div>
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
          <div style={{ fontSize: 250, fontWeight: 800, letterSpacing: "-0.03em", color, transform: `scale(${scale})`, filter: colorMix > 0.5 ? "drop-shadow(0 0 60px #ef444466)" : "none", fontVariantNumeric: "tabular-nums" }}>{shown}</div>
        </AbsoluteFill>
        <div style={{ position: "absolute", bottom: 520, left: 96, right: 96, textAlign: "center", fontSize: 46, fontWeight: 500, color: "#9AA0AA", opacity: cO }}>por una pantalla de $15,000 MXN</div>
      </AbsoluteFill>
    );
  }

  // === LA BIBLIA: #070707 mate, finísima, MAYÚS tracking anchísimo, 1 acento cálido ===
  const color = colorMix > 0.5 ? "#E2543F" : "#B9BCC4";
  return (
    <AbsoluteFill style={{ backgroundColor: "#070707", fontFamily: FONT }}>
      {/* luz volumétrica fría, apenas presente */}
      <AbsoluteFill style={{ background: "radial-gradient(90% 60% at 50% 30%, rgba(70,95,130,0.14) 0%, transparent 62%)" }} />
      <AbsoluteFill style={{ background: "radial-gradient(120% 90% at 50% 100%, transparent 55%, rgba(0,0,0,0.5) 100%)" }} />
      <div style={{ position: "absolute", top: 84, left: 0, right: 0, textAlign: "center", fontSize: 25, fontWeight: 300, letterSpacing: "0.55em", color: "#D9DBDF", paddingLeft: "0.55em" }}>DINERO IA</div>
      <div style={{ position: "absolute", top: 480, left: 0, right: 0, textAlign: "center", fontSize: 27, fontWeight: 250, letterSpacing: "0.6em", color: "#8E939C", opacity: kO, paddingLeft: "0.6em" }}>TERMINAS PAGANDO</div>
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ fontSize: 264, fontWeight: 200, letterSpacing: "-0.01em", color, transform: `scale(${scale})`, fontVariantNumeric: "tabular-nums", textShadow: colorMix > 0.5 ? "0 0 90px rgba(226,84,63,0.28)" : "none" }}>{shown}</div>
      </AbsoluteFill>
      <div style={{ position: "absolute", bottom: 540, left: 0, right: 0, textAlign: "center", fontSize: 27, fontWeight: 250, letterSpacing: "0.42em", color: "#8E939C", opacity: cO, paddingLeft: "0.42em" }}>POR UNA PANTALLA DE $15,000 MXN</div>
      {/* hairline fina de pie, restricción */}
      <div style={{ position: "absolute", bottom: 420, left: 420, right: 420, height: 1, background: "rgba(255,255,255,0.14)", opacity: cO }} />
    </AbsoluteFill>
  );
};
