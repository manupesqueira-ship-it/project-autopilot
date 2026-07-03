import { loadFont } from "@remotion/fonts";
import { noise2D } from "@remotion/noise";
import React from "react";
import { AbsoluteFill, staticFile, useCurrentFrame } from "remotion";
import { CURVE, PAL, TOK } from "./tokens";

// MUNDO DE LA PÁGINA — base compartida de los masters (plan maestro §06 + tablero
// aprobado 2026-07-03). Negro mate, luz volumétrica fría casi imperceptible,
// grano vivo + viñeta, cámara con MASA (Tendril). DM Mono = labels y números
// (mismo lenguaje que la web); grotesca fina para frases.

// Chivo Mono (variable, OFL, Omnibus-Type/AR): CERO LIMPIO — Manuel rechazó el
// cero tachado ("no se ve profesional", 2026-07-03). DM Mono y Roboto Mono lo
// traen cruzado de fábrica (fuentes de código); verificado en píxeles que
// Chivo Mono no. Grotesca-mono geométrica = el carácter del mundo de la página.
loadFont({ family: "ChivoMono", url: staticFile("fonts/ChivoMono-Var.ttf"), weight: "100 900" });

export const MONO = "ChivoMono, 'Cascadia Mono', Consolas, monospace";
export const SANS = "InterVar, Inter, 'Segoe UI', sans-serif";

// Fondo: negro mate + respiración volumétrica fría MUY contenida (igloo, no neón)
export const PageBg: React.FC<{ energy?: number }> = ({ energy = 0.05 }) => {
  const frame = useCurrentFrame();
  const breathe = 1 + 0.12 * Math.sin(frame / 46);
  return (
    <AbsoluteFill style={{ backgroundColor: PAL.bg }}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(${58 * breathe}% ${40 * breathe}% at 50% 38%, rgba(62,92,118,${energy}) 0%, transparent 64%)`,
        }}
      />
      <AbsoluteFill
        style={{
          background: "radial-gradient(80% 50% at 50% 100%, rgba(0,0,0,0.5) 0%, transparent 60%)",
        }}
      />
    </AbsoluteFill>
  );
};

// Grano vivo + viñeta (óptica global; va al FINAL del árbol)
export const Grain: React.FC<{ grain?: number; vignette?: number }> = ({ grain = 0.045, vignette = 0.34 }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none", zIndex: 90 }}>
      <svg width="100%" height="100%" style={{ position: "absolute", inset: 0, opacity: grain, mixBlendMode: "screen" }}>
        <filter id="k2gr">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={frame % 500} stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#k2gr)" />
      </svg>
      <AbsoluteFill style={{ background: `radial-gradient(120% 95% at 50% 44%, transparent 44%, rgba(0,0,0,${vignette}) 100%)` }} />
    </AbsoluteFill>
  );
};

// Cámara con MASA (token camera + curve.mass): push-in lento en TODA la escena.
// Nada llega a su pose rápido; drift determinista mínimo.
export const MassCamera: React.FC<{ children: React.ReactNode; durF: number; seed?: number }> = ({
  children,
  durF,
  seed = 1,
}) => {
  const frame = useCurrentFrame();
  const t = CURVE.mass(Math.min(1, frame / Math.max(1, durF)));
  const scale = 1 + TOK.camera.pushScale * t;
  const dx = noise2D(`k2x${seed}`, frame * 0.011, 0) * TOK.camera.driftPx;
  const dy = noise2D(`k2y${seed}`, 0, frame * 0.009) * TOK.camera.driftPx;
  return (
    <AbsoluteFill style={{ transform: `scale(${scale}) translate(${dx}px, ${dy}px)`, transformOrigin: "50% 44%" }}>
      {children}
    </AbsoluteFill>
  );
};
