import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";

// IglooStage — el mundo igloo.inc (biblia 2026-06-29): negro mate, espacio
// negativo extremo, azules fríos + UN acento esmeralda, luz volumétrica,
// movimiento LENTO. Es el mismo mundo que el mapa de El Salvador aprobado
// (VOID #070707, viñeta, grano fino). Sustituye a StudioScene/PremiumStage en
// los beats de este reel para que TODO se sienta un solo plano coherente.
// El color lo pone el contenido vía `accent`; la sala es fría y vacía.

const W = 1080;
const H = 1920;
const VOID = "#070707";

export const IglooStage: React.FC<{
  children: React.ReactNode;
  accent?: string; // esmeralda de marca por defecto
  glowY?: number; // 0..1 — altura del halo de acento (donde se asienta el contenido)
  drift?: boolean; // deriva lenta de cámara
  grainSeed?: number;
}> = ({ children, accent = "#00D9A5", glowY = 0.52, drift = true, grainSeed = 7 }) => {
  const frame = useCurrentFrame();
  // movimiento lento: deriva mínima (igloo.inc = calma, no parallax agresivo)
  const dx = drift ? Math.sin(frame / 120) * 5 : 0;
  const dy = drift ? Math.cos(frame / 150) * 4 : 0;
  const gid = `igloograin${grainSeed}`;

  return (
    <AbsoluteFill style={{ backgroundColor: VOID, overflow: "hidden" }}>
      {/* luz volumétrica fría desde arriba — azules fríos del bible */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 96% 58% at 50% 20%, rgba(96,142,172,0.11) 0%, rgba(42,62,82,0.05) 38%, transparent 66%)",
        }}
      />
      {/* brasa esmeralda baja, ligada al contenido — UN acento cálido */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 58% 40% at 50% ${glowY * 100}%, ${accent}16 0%, ${accent}08 42%, transparent 70%)`,
          transform: `translate(${dx * 0.5}px, ${dy * 0.5}px)`,
          mixBlendMode: "screen",
        }}
      />
      {/* contenido (capa flotante, deriva suave) */}
      <AbsoluteFill style={{ transform: `translate(${dx}px, ${dy}px)` }}>
        {children}
      </AbsoluteFill>
      {/* viñeta de profundidad (igual que el mapa) */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(120% 80% at 50% 44%, transparent 50%, rgba(0,0,0,0.62) 100%)",
          pointerEvents: "none",
        }}
      />
      {/* grano fino desaturado */}
      <AbsoluteFill style={{ opacity: 0.05, mixBlendMode: "overlay", pointerEvents: "none" }}>
        <svg width={W} height={H}>
          <filter id={gid}>
            <feTurbulence
              type="fractalNoise"
              baseFrequency="0.9"
              numOctaves="2"
              stitchTiles="stitch"
              seed={grainSeed}
            />
            <feColorMatrix type="saturate" values="0" />
          </filter>
          <rect width={W} height={H} filter={`url(#${gid})`} />
        </svg>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
