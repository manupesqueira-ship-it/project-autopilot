import { loadFont } from "@remotion/fonts";
import { noise2D } from "@remotion/noise";
import React from "react";
import { AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame } from "remotion";
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

// Fondo: negro mate + respiración volumétrica fría contenida pero VIVA (igloo).
// Dos ondas desfasadas + centro que deriva: ningún frame idéntico al anterior
// (doctrina "movimiento constante" — los holds largos nunca quedan muertos).
export const PageBg: React.FC<{ energy?: number }> = ({ energy = 0.05 }) => {
  const frame = useCurrentFrame();
  const breathe = 1 + 0.24 * Math.sin(frame / 38);
  const breathe2 = 1 + 0.18 * Math.sin(frame / 61 + 2.1);
  const cx = 50 + 3.5 * Math.sin(frame / 83);
  const cy = 38 + 2.5 * Math.sin(frame / 67 + 1.2);
  return (
    <AbsoluteFill style={{ backgroundColor: PAL.bg }}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(${58 * breathe}% ${40 * breathe}% at ${cx}% ${cy}%, rgba(62,92,118,${energy * 1.4}) 0%, transparent 64%)`,
        }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(${70 * breathe2}% ${30 * breathe2}% at ${100 - cx}% 82%, rgba(46,203,79,${energy * 0.35}) 0%, transparent 58%)`,
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

// PLACA DE MUNDO — hero clip (Kling/i2v) TRATADO al mundo de la página: grade
// oscuro contenido + viñeta + scrim uniforme para que el TEXTO viva encima sin
// empalme (regla dura: texto sobre scrim, nunca sobre imagen ocupada). El clip
// se loopea si el beat dura más que él. Los assets vienen de public/heroes/.
export const WorldPlate: React.FC<{ src: string; dim?: number }> = ({ src, dim = 0.45 }) => (
  <AbsoluteFill>
    <OffthreadVideo
      src={staticFile(src)}
      loop
      muted
      style={{
        width: "100%",
        height: "100%",
        objectFit: "cover",
        filter: "brightness(0.78) saturate(0.85) contrast(1.06)",
      }}
    />
    {/* scrim del mundo: funde el clip al negro mate y abre el carril de texto */}
    <AbsoluteFill style={{ background: `rgba(7,7,7,${dim})` }} />
    <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(7,7,7,0.72) 0%, transparent 30%, transparent 62%, rgba(7,7,7,0.8) 100%)" }} />
  </AbsoluteFill>
);

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

// Cámara con MASA (token camera + curve.mass): push-in que NUNCA se detiene.
// 70% del push con masa + 30% lineal hasta el último frame (la curva de masa
// saturaba al final → cola estática en beats largos, gate anti-slideshow 2026-07-03)
// + drift orgánico lento y respiración micro de escala. Ningún frame quieto.
export const MassCamera: React.FC<{ children: React.ReactNode; durF: number; seed?: number }> = ({
  children,
  durF,
  seed = 1,
}) => {
  const frame = useCurrentFrame();
  const lin = Math.min(1, frame / Math.max(1, durF));
  const t = 0.7 * CURVE.mass(lin) + 0.3 * lin;
  const microScale = 0.004 * Math.sin(frame / 47 + seed);
  const scale = 1 + TOK.camera.pushScale * t + microScale;
  const dx = noise2D(`k2x${seed}`, frame * 0.028, 0) * TOK.camera.driftPx * 1.6;
  const dy = noise2D(`k2y${seed}`, 0, frame * 0.023) * TOK.camera.driftPx * 1.6;
  return (
    <AbsoluteFill style={{ transform: `scale(${scale}) translate(${dx}px, ${dy}px)`, transformOrigin: "50% 44%" }}>
      {children}
    </AbsoluteFill>
  );
};
