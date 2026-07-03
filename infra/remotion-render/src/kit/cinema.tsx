import { noise2D } from "@remotion/noise";
import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { L } from "./look";

// CAPA DE CINE — la óptica global que hace que se lea "filmado", no "navegador".
// <Grade>  : grano vivo (feTurbulence seed=frame) + viñeta radial. Va AL FINAL del árbol.
// <Camera> : push-in lento + drift orgánico determinista. Envuelve el contenido de cada beat.
// Juntas matan el veredicto "slideshow" del gate de movimiento: NINGÚN frame es estático.

export const Grade: React.FC<{ grain?: number; vignette?: number }> = ({ grain = 0.05, vignette = 0.30 }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none", zIndex: 90 }}>
      {/* grano vivo: seed cambia por frame */}
      <svg width="100%" height="100%" style={{ position: "absolute", inset: 0, opacity: grain, mixBlendMode: "screen" }}>
        <filter id="gr">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={frame % 500} stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#gr)" />
      </svg>
      {/* viñeta radial */}
      <AbsoluteFill style={{ background: `radial-gradient(120% 95% at 50% 46%, transparent 46%, rgba(0,0,0,${vignette}) 100%)` }} />
    </AbsoluteFill>
  );
};

// Cámara por beat: push-in 1.00→~1.05 + drift noise ±2-3px (determinista, seed por beat)
export const Camera: React.FC<{
  children: React.ReactNode;
  durF: number;
  seed?: number;
  push?: number;       // escala extra al final (0.05 default)
  drift?: number;      // px de drift orgánico
}> = ({ children, durF, seed = 1, push = 0.05, drift = 2.5 }) => {
  const frame = useCurrentFrame();
  const t = Math.min(1, frame / Math.max(1, durF));
  const scale = 1 + push * t;
  const dx = noise2D(`cx${seed}`, frame * 0.013, 0) * drift;
  const dy = noise2D(`cy${seed}`, 0, frame * 0.011) * drift;
  return (
    <AbsoluteFill style={{ transform: `scale(${scale}) translate(${dx}px, ${dy}px)`, transformOrigin: "50% 46%" }}>
      {children}
    </AbsoluteFill>
  );
};

// Fondo vivo del look A: base + luz volumétrica fría que respira + acento del beat
export const LiveBg: React.FC<{ accent?: string; energy?: number }> = ({ accent = L.kicker, energy = 0.09 }) => {
  const frame = useCurrentFrame();
  const breathe = 1 + 0.18 * Math.sin(frame / 34);
  return (
    <AbsoluteFill style={{ backgroundColor: L.bg }}>
      <AbsoluteFill style={{ background: `radial-gradient(${62 * breathe}% ${42 * breathe}% at 50% 40%, ${accent}${Math.round(energy * 255).toString(16).padStart(2, "0")} 0%, transparent 62%)` }} />
      <AbsoluteFill style={{ background: "radial-gradient(90% 60% at 50% 8%, rgba(66,92,128,0.10) 0%, transparent 55%)" }} />
    </AbsoluteFill>
  );
};
