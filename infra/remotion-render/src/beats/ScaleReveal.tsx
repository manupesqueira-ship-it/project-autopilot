import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";

// ScaleReveal — SI el contenido es "magnitud enorme que hay que dimensionar".
// Rulebook: arrancar cerrado en la cifra que se ve grande (viñeta); al cue, ZOOM-OUT
// (focus+context) que la revela diminuta junto a una barra gigante. Violación de
// expectativa = alto 'wow'. zoom-IN nunca para esto; zoom-OUT = revelación de proporción.

const INK = "#F3EFE7", GREEN = "#10b981", RED = "#ef4444", MUTE = "#9AA0AA";
const FONT = "InterVar, Inter, sans-serif";

export type ScaleRevealProps = {
  smallLabel?: string;
  smallValue?: string;
  bigLabel?: string;
  bigValue?: string;
  cue?: number;
};

export const ScaleReveal: React.FC<ScaleRevealProps> = ({
  smallLabel = "La compra de Trump",
  smallValue = "$1.24 M",
  bigLabel = "Reservas de Bitcoin de EE.UU.",
  bigValue = "$18,000 M",
  cue = 34,
}) => {
  const frame = useCurrentFrame();
  // camara: arranca cerrada en la barra chica (scale 2.4, centrada en ella) -> se aleja a 1.0
  const cam = interpolate(frame, [cue, cue + 34], [2.4, 1.0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
  // la barra chica está a la izquierda-abajo; la cámara arranca centrada en su punta
  const smallH = 150;   // px (diminuta en el layout real)
  const bigH = 1180;    // px (gigante)
  const baseY = 1500;
  const camOX = 360, camOY = baseY - smallH; // punto que la cámara mantiene centrado al inicio

  const bigGrow = interpolate(frame, [cue + 10, cue + 40], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const bigLabelO = interpolate(frame, [cue + 34, cue + 46], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const smallLabelO = interpolate(frame, [8, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#08090B", fontFamily: FONT, overflow: "hidden" }}>
      <div style={{ position: "absolute", top: 78, left: 96, fontSize: 27, fontWeight: 700, letterSpacing: "0.28em", color: INK, zIndex: 5 }}>DINERO&nbsp;IA</div>

      {/* mundo escalado por la "cámara" */}
      <div style={{ position: "absolute", inset: 0, transform: `scale(${cam})`, transformOrigin: `${camOX}px ${camOY}px` }}>
        {/* barra chica */}
        <div style={{ position: "absolute", left: camOX - 90, top: baseY - smallH, width: 180, height: smallH, background: GREEN, borderRadius: 6 }} />
        <div style={{ position: "absolute", left: camOX - 90, top: baseY - smallH - 54, width: 180, textAlign: "center", fontSize: 34, fontWeight: 800, color: GREEN, opacity: smallLabelO }}>{smallValue}</div>

        {/* barra gigante */}
        <div style={{ position: "absolute", left: 720 - 110, top: baseY - bigH * bigGrow, width: 220, height: bigH * bigGrow, background: RED, borderRadius: 8 }} />
        <div style={{ position: "absolute", left: 720 - 110, top: baseY - bigH - 54, width: 220, textAlign: "center", fontSize: 40, fontWeight: 800, color: RED, opacity: bigLabelO }}>{bigValue}</div>

        {/* base line */}
        <div style={{ position: "absolute", left: 120, top: baseY, width: 840, height: 3, background: "#2B2F38" }} />
      </div>

      {/* etiquetas fijas abajo */}
      <div style={{ position: "absolute", bottom: 150, left: 96, right: 96, textAlign: "center", fontSize: 40, fontWeight: 600, color: INK, opacity: bigLabelO }}>{smallLabel} vs {bigLabel}</div>
    </AbsoluteFill>
  );
};
